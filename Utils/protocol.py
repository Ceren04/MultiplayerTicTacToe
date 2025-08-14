import json
import time
from enum import Enum

class MessageType(Enum):
    """Network mesaj türleri"""
    MOVE = "move"
    GAME_STATE = "game_state"
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    GAME_START = "game_start"
    GAME_END = "game_end"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    CHAT = "chat"
    WELCOME = "welcome"

class GameProtocol:
    """
    Network communication protocol for Tic-Tac-Toe
    JSON tabanlı mesaj serialization/deserialization
    """
    
    @staticmethod
    def serialize_move(row, col, player):
        """
        Oyuncu hamlesini network formatına serialize et
        
        Args:
            row (int): Satır koordinatı (0-2)
            col (int): Sütun koordinatı (0-2) 
            player (Player): Hamleyi yapan oyuncu
            
        Returns:
            str: JSON string formatında serialize edilmiş hamle
        """
        message = {
            "type": MessageType.MOVE.value,
            "timestamp": time.time(),
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
        return json.dumps(message)
    
    @staticmethod
    def serialize_game_state(board, current_player, game_status="playing", winner=None, move_count=0):
        """
        Oyun durumunu network formatına serialize et
        
        Args:
            board (list): 3x3 board durumu
            current_player (str): Mevcut oyuncu symbolu
            game_status (str): Oyun durumu
            winner (str, optional): Kazanan oyuncu
            move_count (int): Toplam hamle sayısı
            
        Returns:
            str: JSON string formatında serialize edilmiş game state
        """
        message = {
            "type": MessageType.GAME_STATE.value,
            "timestamp": time.time(),
            "data": {
                "board": board,
                "current_player": current_player,
                "game_status": game_status,
                "winner": winner,
                "move_count": move_count,
                "is_game_over": winner is not None
            }
        }
        return json.dumps(message)
    
    @staticmethod
    def serialize_player_join(player, room_id=None):
        """
        Oyuncu katılma mesajını serialize et
        
        Args:
            player (Player): Katılan oyuncu
            room_id (str, optional): Oyun odası ID'si
            
        Returns:
            str: JSON string formatında serialize edilmiş join mesajı
        """
        message = {
            "type": MessageType.PLAYER_JOIN.value,
            "timestamp": time.time(),
            "data": {
                "player": {
                    "id": player.player_id,
                    "symbol": player.symbol,
                    "name": player.name
                },
                "room_id": room_id
            }
        }
        return json.dumps(message)
    
    @staticmethod
    def serialize_error(error_message, error_code=None):
        """
        Hata mesajını serialize et
        
        Args:
            error_message (str): Hata mesajı
            error_code (str, optional): Hata kodu
            
        Returns:
            str: JSON string formatında serialize edilmiş hata mesajı
        """
        message = {
            "type": MessageType.ERROR.value,
            "timestamp": time.time(),
            "data": {
                "message": error_message,
                "code": error_code
            }
        }
        return json.dumps(message)
    
    @staticmethod
    def serialize_game_start(players, room_id=None):
        """
        Oyun başlama mesajını serialize et
        
        Args:
            players (list): Oyuncu listesi
            room_id (str, optional): Oyun odası ID'si
            
        Returns:
            str: JSON string formatında serialize edilmiş başlama mesajı
        """
        message = {
            "type": MessageType.GAME_START.value,
            "timestamp": time.time(),
            "data": {
                "players": [
                    {
                        "id": player.player_id,
                        "symbol": player.symbol,
                        "name": player.name
                    } for player in players
                ],
                "room_id": room_id,
                "starting_player": "X"
            }
        }
        return json.dumps(message)
    
    @staticmethod
    def serialize_game_end(winner, final_board, move_count):
        """
        Oyun bitiş mesajını serialize et
        
        Args:
            winner (str): Kazanan oyuncu symbolu veya "tie"
            final_board (list): Final board durumu
            move_count (int): Toplam hamle sayısı
            
        Returns:
            str: JSON string formatında serialize edilmiş bitiş mesajı
        """
        message = {
            "type": MessageType.GAME_END.value,
            "timestamp": time.time(),
            "data": {
                "winner": winner,
                "final_board": final_board,
                "move_count": move_count,
                "game_completed": True
            }
        }
        return json.dumps(message)
    
    @staticmethod
    def deserialize_message(json_data):
        """
        JSON string'i mesaj objesine deserialize et
        
        Args:
            json_data (str): JSON formatında mesaj
            
        Returns:
            dict: Parse edilmiş mesaj objesi
            None: Parse hatası durumunda
        """
        try:
            message = json.loads(json_data)
            
            # Mesaj formatı kontrolü
            if not isinstance(message, dict):
                raise ValueError("Mesaj dict formatında olmalı")
            
            if "type" not in message:
                raise ValueError("Mesaj type field'ı içermeli")
            
            if "data" not in message:
                raise ValueError("Mesaj data field'ı içermeli")
            
            # Message type kontrolü
            message_type = message["type"]
            if not any(msg_type.value == message_type for msg_type in MessageType):
                raise ValueError(f"Geçersiz mesaj türü: {message_type}")
            
            return message
            
        except json.JSONDecodeError as e:
            print(f"JSON parse hatası: {e}")
            return None
        except ValueError as e:
            print(f"Mesaj format hatası: {e}")
            return None
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            return None
    
    @staticmethod
    def extract_move_data(message):
        """
        Move mesajından hamle bilgilerini çıkar
        
        Args:
            message (dict): Deserialize edilmiş move mesajı
            
        Returns:
            tuple: (row, col, player_data) veya None
        """
        if message and message.get("type") == MessageType.MOVE.value:
            data = message.get("data", {})
            return (
                data.get("row"),
                data.get("col"), 
                data.get("player")
            )
        return None
    
    @staticmethod
    def extract_game_state_data(message):
        """
        Game state mesajından oyun durumu bilgilerini çıkar
        
        Args:
            message (dict): Deserialize edilmiş game state mesajı
            
        Returns:
            dict: Game state data veya None
        """
        if message and message.get("type") == MessageType.GAME_STATE.value:
            return message.get("data")
        return None
    
    @staticmethod
    def validate_move_message(message):
        """
        Move mesajının geçerliliğini kontrol et
        
        Args:
            message (dict): Kontrol edilecek mesaj
            
        Returns:
            bool: Mesaj geçerli mi?
        """
        if not message or message.get("type") != MessageType.MOVE.value:
            return False
        
        data = message.get("data", {})
        
        # Koordinat kontrolü
        row = data.get("row")
        col = data.get("col")
        
        if not isinstance(row, int) or not isinstance(col, int):
            return False
        
        if not (0 <= row <= 2) or not (0 <= col <= 2):
            return False
        
        # Player bilgisi kontrolü
        player = data.get("player")
        if not player or not isinstance(player, dict):
            return False
        
        required_player_fields = ["id", "symbol", "name"]
        if not all(field in player for field in required_player_fields):
            return False
        
        return True
    
    @staticmethod
    def create_heartbeat():
        """
        Heartbeat mesajı oluştur (connection canlılığı için)
        
        Returns:
            str: JSON heartbeat mesajı
        """
        message = {
            "type": MessageType.HEARTBEAT.value,
            "timestamp": time.time(),
            "data": {}
        }
        return json.dumps(message)