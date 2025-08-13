import asyncio
import websockets
import json
from enum import Enum
from Utils.protocol import GameProtocol, MessageType
from Utils.validator import GameValidator

class ClientStatus(Enum):
    DISCONNECTED = 1
    CONNECTING = 2
    CONNECTED = 3


class GameClient:
    def __init__(self, server_url=""):
        self.server_url = server_url
        self.websocket = None
        self.status = ClientStatus.DISCONNECTED
        self.player_symbol = None
        self.room_id = None

    async def connect(self):
        """
        Server'a WebSocket connection kur
        Authentication/handshake işlemi
        
        Returns:
            bool: Bağlantı başarılı mı?
        """
        try:
            self.status = ClientStatus.CONNECTING
            print(f"Bağlanılıyor: {self.server_url}")
            
            self.websocket = await websockets.connect(self.server_url)
            self.status = ClientStatus.CONNECTED
            print("Server'a başarıyla bağlanıldı!")
            return True
            
        except websockets.exceptions.InvalidURI:
            print("Geçersiz server URL'i!")
            self.status = ClientStatus.DISCONNECTED
            return False
        except websockets.exceptions.ConnectionRefused:
            print("Server'a bağlanılamadı! Server çalışıyor mu?")
            self.status = ClientStatus.DISCONNECTED
            return False
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            self.status = ClientStatus.DISCONNECTED
            return False

    async def disconnect(self):
        """
        Server bağlantısını temiz şekilde kapat
        Resources'ları temizle
        
        Returns:
            bool: Disconnect başarılı mı?
        """
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            self.status = ClientStatus.DISCONNECTED
            print("Server bağlantısı kapatıldı.")
            return True
        except Exception as e:
            print(f"Disconnect hatası: {e}")
            return False
    
    async def send_message(self, message):
        """
        Server'a mesaj gönder
        
        Args:
            message (dict): Gönderilecek mesaj
            
        Returns:
            bool: Gönderme başarılı mı?
        """
        if self.websocket and self.status == ClientStatus.CONNECTED:
            try:
                data = json.dumps(message)
                await self.websocket.send(data)
                return True
            except websockets.exceptions.ConnectionClosed:
                print("Bağlantı kesildi!")
                self.status = ClientStatus.DISCONNECTED
                return False
            except Exception as e:
                print(f"Mesaj gönderme hatası: {e}")
                return False
        else:
            print("Bağlantı yok veya kapalı!")
            return False

    async def send_player_join(self, player):
        """
        Oyuncunun katılma isteğini server'a gönder
        
        Args:
            player (Player): Katılacak oyuncu
            
        Returns:
            bool: Gönderme başarılı mı?
        """
        try:
            join_message = GameProtocol.serialize_player_join(player, self.room_id)
            message_dict = json.loads(join_message)
            return await self.send_message(message_dict)
        except Exception as e:
            print(f"Player join mesajı gönderme hatası: {e}")
            return False

    async def send_move(self, player, row, col):
        """
        Hamleyi JSON olarak serialize et ve server'a gönder
        
        Args:
            player (Player): Hamleyi yapan oyuncu
            row (int): Satır koordinatı
            col (int): Sütun koordinatı
            
        Returns:
            bool: Gönderme başarılı mı?
        """
        try:
            # Koordinatları validate et
            valid, error = GameValidator.validate_coordinates(row, col)
            if not valid:
                print(f"Geçersiz koordinat: {error}")
                return False
            
            message = {
                "type": MessageType.MOVE.value,
                "data": {
                    "row": row,
                    "col": col,
                    "player": {
                        "id": player.player_id,
                        "symbol": player.symbol,
                        "name": player.name
                    }
                }
            }
            return await self.send_message(message)
            
        except Exception as e:
            print(f"Move gönderme hatası: {e}")
            return False

    async def listen_for_updates(self):
        """
        Server'dan gelen mesajları dinle
        Game state update'lerini işle
        
        Returns:
            str: Gelen mesaj (JSON string) veya None
        """
        while self.status == ClientStatus.CONNECTED:
            try:
                if self.websocket:
                    message = await self.websocket.recv()
                    return message
                else:
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                print("Server bağlantısı kesildi!")
                self.status = ClientStatus.DISCONNECTED
                break
            except Exception as e:
                print(f"Mesaj dinleme hatası: {e}")
                break
        
        return None

    async def send_heartbeat(self):
        """
        Server'a heartbeat gönder (connection canlılığı için)
        
        Returns:
            bool: Gönderme başarılı mı?
        """
        try:
            heartbeat_message = GameProtocol.create_heartbeat()
            message_dict = json.loads(heartbeat_message)
            return await self.send_message(message_dict)
        except Exception as e:
            print(f"Heartbeat gönderme hatası: {e}")
            return False

    def get_user_input(self):
        """
        Kullanıcıdan hamle koordinatlarını al (network client için özel)
        Return: (row, col) tuple veya None (quit için)
        """
        while True:
            try:
                move_input = input("Hamlenizi girin (satır,sütun) veya 'q' (çıkış için): ").strip()
                
                if move_input.lower() == 'q':
                    return None
                
                if not move_input:
                    print("Lütfen bir değer girin!")
                    continue
                
                if ',' not in move_input:
                    print("Lütfen virgülle ayırarak girin! (örnek: 1,2)")
                    continue
                
                parts = move_input.split(',')
                if len(parts) != 2:
                    print("Tam iki değer girin! (örnek: 1,2)")
                    continue
                
                row = int(parts[0].strip())
                col = int(parts[1].strip())
                
                # Koordinat validation
                valid, error = GameValidator.validate_coordinates(row, col)
                if not valid:
                    print(f"Geçersiz koordinat: {error}")
                    continue
                
                return (row, col)
                
            except ValueError:
                print("Geçerli sayılar girin!")
            except KeyboardInterrupt:
                print("\nÇıkılıyor...")
                return None
            except Exception as e:
                print(f"Input hatası: {e}")

    def display_board(self, board):
        """
        Mevcut board durumunu terminal'de göster
        
        Args:
            board (list): 3x3 board matrix
        """
        try:
            if not board:
                print("Board verisi yok!")
                return
            
            print("\n   0   1   2")  # Sütun numaraları
            print("  -----------")
            
            for row_idx in range(3):
                print(f"{row_idx}|", end="")
                
                for col_idx in range(3):
                    # Hücre içeriği
                    cell = board[row_idx][col_idx] if row_idx < len(board) and col_idx < len(board[row_idx]) else None
                    if cell is None:
                        display_char = " "
                    else:
                        display_char = cell
                    
                    print(f" {display_char} ", end="")
                    
                    # Sütun ayırıcısı
                    if col_idx < 2:
                        print("|", end="")
                
                print()  # Satır sonu
                
                # Satır ayırıcısı (son satır değilse)
                if row_idx < 2:
                    print("  -----------")
            
            print("  -----------\n")
            
        except Exception as e:
            print(f"Board display hatası: {e}")

    def handle_server_message(self, message):
        """
        Server'dan gelen mesajları parse et ve handle et
        
        Args:
            message (str): JSON mesaj string'i
            
        Returns:
            dict: Parse edilmiş mesaj veya None
        """
        try:
            parsed_message = GameProtocol.deserialize_message(message)
            if not parsed_message:
                print("Geçersiz mesaj formatı!")
                return None
            
            message_type = parsed_message.get("type")
            data = parsed_message.get("data", {})
            
            print(f"Server mesajı: {message_type}")
            
            if message_type == "welcome":
                print(f"✅ {data.get('message', 'Hoş geldiniz!')}")
                self.room_id = data.get("room_id")
                
            elif message_type == "waiting":
                print(f"⏳ {data.get('message', 'Bekleniyor...')}")
                self.player_symbol = data.get("your_symbol")
                if self.player_symbol:
                    print(f"🎯 Sizin sembolünüz: {self.player_symbol}")
                
            elif message_type == MessageType.GAME_START.value:
                print("🎮 Oyun başlıyor!")
                players = data.get("players", [])
                for player in players:
                    print(f"👤 {player.get('name')} ({player.get('symbol')})")
                
            elif message_type == MessageType.GAME_STATE.value:
                # Game state göster
                board = data.get("board")
                if board:
                    self.display_board(board)
                
                current_player = data.get("current_player")
                if current_player:
                    if current_player == self.player_symbol:
                        print("🎯 SİZİN SIRANIZ!")
                    else:
                        print(f"⏳ Rakibin sırası... ({current_player})")
                
            elif message_type == MessageType.GAME_END.value:
                winner = data.get("winner")
                print("\n" + "="*50)
                if winner == "tie":
                    print("🤝 BERABERE!")
                elif winner == self.player_symbol:
                    print("🎉 KAZANDINIZ!")
                else:
                    print(f"😞 Kaybettiniz. Kazanan: {winner}")
                print("="*50)
                
            elif message_type == MessageType.ERROR.value:
                error_msg = data.get("message", "Bilinmeyen hata")
                print(f"❌ HATA: {error_msg}")
                
            elif message_type == MessageType.HEARTBEAT.value:
                # Heartbeat response - sessizce handle et
                pass
                
            else:
                print(f"⚠️ Bilinmeyen mesaj türü: {message_type}")
            
            return parsed_message
            
        except Exception as e:
            print(f"Mesaj handling hatası: {e}")
            return None

    def is_connected(self):
        """
        Bağlantı durumunu kontrol et
        
        Returns:
            bool: Bağlı mı?
        """
        return self.status == ClientStatus.CONNECTED and self.websocket is not None

    async def game_loop(self, player):
        """
        Client tarafında ana oyun döngüsü
        
        Args:
            player (Player): Local player
        """
        try:
            print("Oyun döngüsü başlatılıyor...")
            
            # İlk olarak player join gönder
            if not await self.send_player_join(player):
                print("Player join gönderilemedi!")
                return
            
            # Ana oyun döngüsü
            while self.is_connected():
                # Server'dan mesaj bekle
                message = await self.listen_for_updates()
                if not message:
                    break
                
                # Mesajı handle et
                parsed_message = self.handle_server_message(message)
                if not parsed_message:
                    continue
                
                message_type = parsed_message.get("type")
                data = parsed_message.get("data", {})
                
                # Eğer bizim sıramızsa ve oyun devam ediyorsa
                if (message_type == MessageType.GAME_STATE.value and 
                    data.get("current_player") == self.player_symbol and
                    not data.get("is_game_over", False)):
                    
                    # Kullanıcıdan hamle al
                    move = self.get_user_input()
                    if move is None:  # Quit
                        break
                    
                    row, col = move
                    # Hamleyi gönder
                    if not await self.send_move(player, row, col):
                        print("Hamle gönderilemedi!")
                
                # Oyun bittiyse döngüden çık
                elif message_type == MessageType.GAME_END.value:
                    input("Devam etmek için Enter'a basın...")
                    break
            
        except KeyboardInterrupt:
            print("\nOyun döngüsü kullanıcı tarafından durduruldu.")
        except Exception as e:
            print(f"Oyun döngüsü hatası: {e}")
        finally:
            await self.disconnect()


# Test ve standalone kullanım için
async def main():
    """
    Client'ı test et
    """
    try:
        server_url = input("Server URL (ws://localhost:8765): ").strip()
        if not server_url:
            server_url = "ws://localhost:8765"
        
        player_name = input("Adınızı girin: ").strip()
        if not player_name:
            player_name = "Test Oyuncusu"
        
        # Client oluştur
        client = GameClient(server_url)
        
        # Bağlan
        if await client.connect():
            from player import Player
            player = Player(player_id=1, symbol="X", name=player_name)
            
            # Oyun döngüsünü başlat
            await client.game_loop(player)
        else:
            print("Bağlantı kurulamadı!")
            
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
    except Exception as e:
        print(f"Ana loop hatası: {e}")


if __name__ == "__main__":
    asyncio.run(main())