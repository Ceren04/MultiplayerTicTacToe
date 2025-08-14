import asyncio
import websockets
import json
import uuid
from enum import Enum
from protocol import GameProtocol, MessageType
from player import Player
from game_logic import Game
from validator import GameValidator


class Status(Enum):
    WAITING = 1
    IN_PROGRESS = 2
    FINISHED = 3

    
class GameServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port 
        self.clients = set()
        self.game_rooms = {}  # {room_id : GameRoom}
        self.waiting_room = None  # Bekleyen oyuncular için
        
    async def handle_client(self, websocket, path):
        """
        Yeni client connection'ını işle ve message loop'unu başlat
        """
        self.clients.add(websocket)
        print(f"Yeni client bağlandı. Toplam client: {len(self.clients)}")
        
        try:
            # Client'ı waiting room'a ekle
            if not self.waiting_room or self.waiting_room.is_full():
                self.waiting_room = self.create_game_room()
            
            # Hoş geldin mesajı gönder
            welcome_message = {
                "type": "welcome",
                "data": {
                    "message": "Server'a hoş geldiniz!",
                    "room_id": self.waiting_room.room_id
                }
            }
            await websocket.send(json.dumps(welcome_message))
            
            # Message handling loop
            async for message in websocket:
                await self.process_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            print("Client bağlantısı kesildi")
        except Exception as e:
            print(f"Client handling hatası: {e}")
        finally:
            self.clients.remove(websocket)
            # Client'ı tüm room'lardan çıkar
            for room in self.game_rooms.values():
                room.remove_player(websocket)
    
    async def process_client_message(self, websocket, message):
        """
        Client'tan gelen mesajları işle
        
        Args:
            websocket: Client websocket
            message (str): JSON mesaj
        """
        try:
            # Mesajı parse et
            parsed_message = GameProtocol.deserialize_message(message)
            if not parsed_message:
                await self.send_error(websocket, "Geçersiz mesaj formatı")
                return
            
            message_type = parsed_message.get("type")
            data = parsed_message.get("data", {})
            
            print(f"Mesaj alındı: {message_type}")
            
            if message_type == MessageType.PLAYER_JOIN.value:
                await self.handle_player_join(websocket, data)
                
            elif message_type == MessageType.MOVE.value:
                await self.handle_player_move(websocket, data)
                
            elif message_type == MessageType.HEARTBEAT.value:
                # Heartbeat'e response gönder
                await websocket.send(GameProtocol.create_heartbeat())
                
            else:
                await self.send_error(websocket, f"Bilinmeyen mesaj türü: {message_type}")
                
        except Exception as e:
            print(f"Mesaj işleme hatası: {e}")
            await self.send_error(websocket, "Mesaj işleme hatası")
    
    async def handle_player_join(self, websocket, data):
        """
        Oyuncu katılma isteğini işle
        
        Args:
            websocket: Client websocket
            data (dict): Player join verisi
        """
        try:
            # Player data validation
            player_data = data.get("player", {})
            valid, error = GameValidator.validate_player_data(player_data)
            
            if not valid:
                await self.send_error(websocket, f"Geçersiz oyuncu verisi: {error}")
                return
            
            # Player'ı waiting room'a ekle
            if self.waiting_room and not self.waiting_room.is_full():
                # Symbol ata (ilk gelen X, ikinci O)
                symbol = "X" if len(self.waiting_room.players) == 0 else "O"
                
                player_info = {
                    "id": player_data.get("id"),
                    "name": player_data.get("name"),
                    "symbol": symbol
                }
                
                if self.waiting_room.add_player(websocket, player_info):
                    print(f"Oyuncu eklendi: {player_info['name']} ({symbol})")
                    
                    # Room dolduysa oyunu başlat
                    if self.waiting_room.is_full():
                        await self.start_room_game(self.waiting_room)
                    else:
                        # Oyuncu bekleme mesajı gönder
                        waiting_message = {
                            "type": "waiting",
                            "data": {
                                "message": "İkinci oyuncuyu bekliyorsunuz...",
                                "your_symbol": symbol
                            }
                        }
                        await websocket.send(json.dumps(waiting_message))
                else:
                    await self.send_error(websocket, "Room'a eklenemedi")
            else:
                await self.send_error(websocket, "Müsait room yok")
                
        except Exception as e:
            print(f"Player join hatası: {e}")
            await self.send_error(websocket, "Katılma işlemi başarısız")
    
    async def handle_player_move(self, websocket, data):
        """
        Oyuncu hamlesini işle
        
        Args:
            websocket: Client websocket
            data (dict): Move verisi
        """
        try:
            # Player'ın hangi room'da olduğunu bul
            player_room = None
            player_info = None
            
            for room in self.game_rooms.values():
                for player in room.players:
                    if player["websocket"] == websocket:
                        player_room = room
                        player_info = player["player_info"]
                        break
                if player_room:
                    break
            
            if not player_room or not player_info:
                await self.send_error(websocket, "Oyuncu room'da bulunamadı")
                return
            
            # Move verilerini çıkar
            row = data.get("row")
            col = data.get("col")
            
            # Koordinat validation
            valid, error = GameValidator.validate_coordinates(row, col)
            if not valid:
                await self.send_error(websocket, f"Geçersiz koordinat: {error}")
                return
            
            # Game'den hamleyi işle
            if hasattr(player_room, 'game') and player_room.game:
                # Current player kontrolü
                if player_room.game.current_player != player_info["symbol"]:
                    await self.send_error(websocket, "Sizin sıranız değil!")
                    return
                
                # Player object oluştur
                temp_player = Player(
                    player_id=player_info["id"],
                    symbol=player_info["symbol"],
                    name=player_info["name"]
                )
                
                # Hamleyi işle
                success, message, game_state = player_room.game.process_move(temp_player, row, col)
                
                if success:
                    # Game state'i room'a broadcast et
                    await player_room.broadcast_game_state(game_state)
                    
                    # Oyun bittiyse end mesajı gönder
                    if game_state.get("is_game_over"):
                        end_message = GameProtocol.serialize_game_end(
                            winner=game_state.get("winner"),
                            final_board=game_state.get("board"),
                            move_count=game_state.get("move_count", 0)
                        )
                        await player_room.broadcast(json.loads(end_message))
                        player_room.status = Status.FINISHED
                else:
                    await self.send_error(websocket, message)
            else:
                await self.send_error(websocket, "Oyun henüz başlamadı")
                
        except Exception as e:
            print(f"Move handling hatası: {e}")
            await self.send_error(websocket, "Hamle işleme hatası")
    
    async def start_room_game(self, room):
        """
        Room'daki oyunu başlat
        
        Args:
            room (GameRoom): Oyun odası
        """
        try:
            if len(room.players) == 2:
                # Player objelerini oluştur
                player1_info = room.players[0]["player_info"]
                player2_info = room.players[1]["player_info"]
                
                player1 = Player(
                    player_id=player1_info["id"],
                    symbol=player1_info["symbol"],
                    name=player1_info["name"]
                )
                
                player2 = Player(
                    player_id=player2_info["id"],
                    symbol=player2_info["symbol"], 
                    name=player2_info["name"]
                )
                
                # Game objesi oluştur
                room.game = Game(player1, player2)
                room.status = Status.IN_PROGRESS
                
                print(f"Oyun başlatıldı: {player1.name} vs {player2.name}")
                
                # Game start mesajı gönder
                start_message = GameProtocol.serialize_game_start([player1, player2], room.room_id)
                await room.broadcast(json.loads(start_message))
                
                # İlk game state'i gönder
                initial_state = room.game.get_game_state()
                await room.broadcast_game_state(initial_state)
                
        except Exception as e:
            print(f"Game start hatası: {e}")
    
    async def send_error(self, websocket, error_message):
        """
        Client'a hata mesajı gönder
        
        Args:
            websocket: Client websocket
            error_message (str): Hata mesajı
        """
        try:
            error_msg = GameProtocol.serialize_error(error_message)
            await websocket.send(error_msg)
        except Exception as e:
            print(f"Error gönderme hatası: {e}")
            
    async def start_server(self):
        """
        WebSocket server'ı başlat
        """
        print(f"Server başlatılıyor: {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"Server çalışıyor: ws://{self.host}:{self.port}")
            print("Oyuncular bekleniyor... (Ctrl+C ile çıkış)")
            
            # Server'ı sürekli çalışır durumda tut
            await asyncio.Future()  # Run forever
            
    def create_game_room(self):
        """
        Yeni oyun odası oluştur
        Return: GameRoom instance
        """
        gameroom = GameRoom()
        self.game_rooms[gameroom.room_id] = gameroom
        print(f"Yeni room oluşturuldu: {gameroom.room_id}")
        return gameroom


class GameRoom:
    room_counter = 0  # Static variable for unique room IDs

    def __init__(self, max_players=2):
        GameRoom.room_counter += 1
        self.room_id = GameRoom.room_counter  # Unique ID
        self.max_players = max_players
        self.status = Status.WAITING
        self.game = None  # Game instance
        self.players = []  # list of dicts: {"websocket": ws, "player_info": {...}}

    def add_player(self, websocket, player_info):
        """
        Room'a oyuncu ekle
        
        Args:
            websocket: Client websocket
            player_info (dict): Oyuncu bilgileri
            
        Returns:
            bool: Başarılı ekleme
        """
        if websocket and player_info and not self.is_full():
            self.players.append({
                "websocket": websocket,
                "player_info": player_info
            })
            return True
        return False

    def remove_player(self, websocket):
        """
        Room'dan oyuncu çıkar
        
        Args:
            websocket: Çıkarılacak client websocket
            
        Returns:
            bool: Başarılı çıkarma
        """
        if websocket:
            for player in self.players:
                if player["websocket"] == websocket:
                    self.players.remove(player)
                    print(f"Oyuncu room'dan çıkarıldı: Room {self.room_id}")
                    return True
        return False

    def is_full(self):
        """
        Room'un dolu olup olmadığını kontrol et
        
        Returns:
            bool: Room dolu mu?
        """
        return len(self.players) >= self.max_players

    async def broadcast(self, message, exclude_ws=None):
        """
        Room'daki tüm oyunculara mesaj gönder
        
        Args:
            message (dict): Gönderilecek mesaj
            exclude_ws: Hariç tutulacak websocket (opsiyonel)
        """
        if not self.players:
            return

        data = json.dumps(message)

        websockets_to_send = [
            player["websocket"]
            for player in self.players
            if player["websocket"] != exclude_ws
        ]

        if websockets_to_send:
            await asyncio.gather(
                *(ws.send(data) for ws in websockets_to_send),
                return_exceptions=True
            )

    async def broadcast_game_state(self, game_state):
        """
        Game state'i room'daki tüm oyunculara gönder
        
        Args:
            game_state (dict): Oyun durumu
        """
        try:
            message = {
                "type": MessageType.GAME_STATE.value,
                "data": game_state
            }
            await self.broadcast(message)
        except Exception as e:
            print(f"Game state broadcast hatası: {e}")
        
        
async def main():
    """
    Server'ı başlat
    """
    server = GameServer()
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\nServer kapatılıyor...")
    except Exception as e:
        print(f"Server hatası: {e}")


if __name__ == "__main__":
    asyncio.run(main())