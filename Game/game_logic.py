from board import GameBoard
from enum import Enum

class Status(Enum):
    FINISHED = 1
    STARTED = 2
    WAITING = 3

class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.game_board = GameBoard()
        self.current_player = "X"  # Symbol olarak tut (player1 = X, player2 = O)
        self.game_status = Status.STARTED
        self.move_count = 0
        self.winner = None
        
    def start_game(self):
        """
        Oyunu başlat ve ilk durumu göster
        """
        print("---------------------------TicTacToe---------------------------------")
        print(f"Oyun başlıyor! {self.player1.name} (X) vs {self.player2.name} (O)")
        print(f"İlk sıra: {self.current_player}")
        self.game_board.display()
        
    def process_move(self, player, row, col):
        """
        Oyuncunun hamlesini işle ve oyun durumunu güncelle
        
        Adımlar:
        1. Bu oyuncunun sırası mı kontrol et
        2. Hamle geçerli mi kontrol et (board.is_valid_move)
        3. Hamleyi board'a uygula (board.make_move)
        4. Kazanan var mı kontrol et (board.check_winner)
        5. Oyun bittiyse game_status'u FINISHED yap
        6. Sırayı diğer oyuncuya geçir (switch_turn)
        7. Return: (success: bool, message: str, game_state: dict)
        """
        # 1. Sıra kontrolü
        if not player.is_turn(self.current_player):
            return False, "Sizin sıranız değil!", self.get_game_state()
        
        # 2. Hamle geçerliliği kontrolü
        if not self.game_board.is_valid_move(row, col):
            return False, "Geçersiz hamle! Bu pozisyon dolu veya koordinatlar yanlış.", self.get_game_state()
        
        # 3. Hamleyi uygula
        if self.game_board.make_move(row, col, player.symbol):
            self.move_count += 1
            
            # 4. Kazanan kontrolü
            winner_result = self.game_board.check_winner()
            
            if winner_result["state"]:  # Kazanan var
                self.winner = winner_result["player"]
                self.game_status = Status.FINISHED
                return True, f"Oyun bitti! Kazanan: {self.winner}", self.get_game_state()
            
            # 5. Berabere kontrolü
            if self.game_board.is_board_full():
                self.winner = "tie"
                self.game_status = Status.FINISHED
                return True, "Oyun bitti! Berabere!", self.get_game_state()
            
            # 6. Sırayı değiştir
            self.switch_turn()
            return True, f"Hamle başarılı! Sıra: {self.current_player}", self.get_game_state()
        
        else:
            return False, "Hamle yapılamadı!", self.get_game_state()
    
    def switch_turn(self):
        """
        Sırayı diğer oyuncuya geçir
        
        Logic:
        - Eğer current_player == "X" ise -> "O"'ya geçir
        - Eğer current_player == "O" ise -> "X"'e geçir
        
        Kullanım:
        - Her başarılı hamle sonrası çağrılır
        - Multiplayer'da critical: sıra takibi için
        """
        self.current_player = "O" if self.current_player == "X" else "X"
        
    def end_game(self):
        """
        Oyunu sonlandır ve sonuçları göster
        Kaynakları temizle
        """
        self.game_status = Status.FINISHED
        
        print("\n" + "="*50)
        print("           OYUN SONUÇLARI")
        print("="*50)
        
        # Final board'u göster
        self.game_board.display()
        
        # Sonuçları göster
        if self.winner == "tie":
            print("🤝 BERABERE!")
            print("İyi oyun, her iki taraf da başarılı!")
        elif self.winner:
            winner_player = self.player1 if self.winner == self.player1.symbol else self.player2
            print(f"🎉 KAZANAN: {winner_player.name} ({self.winner})!")
            print(f"Tebrikler {winner_player.name}!")
        else:
            print("❌ Oyun tamamlanamadı.")
        
        print(f"Toplam hamle sayısı: {self.move_count}")
        print("="*50)
        
        # Board'u reset et (yeni oyun için)
        self.game_board.reset()
        
    def get_game_state(self):
        """
        Mevcut oyun durumunu network için serialize edilebilir format'ta döndür
        Return: dictionary with game state
        """
        winner_result = self.game_board.check_winner()
        
        return {
            "board": [row[:] for row in self.game_board.board],  # Deep copy
            "current_player": self.current_player,
            "game_status": self.game_status.name,
            "winner": self.winner,
            "move_count": self.move_count,
            "is_game_over": self.game_status == Status.FINISHED,
            "players": {
                "player1": {
                    "name": self.player1.name,
                    "symbol": self.player1.symbol,
                    "id": self.player1.player_id
                },
                "player2": {
                    "name": self.player2.name, 
                    "symbol": self.player2.symbol,
                    "id": self.player2.player_id
                }
            }
        }
    
    def get_current_player_object(self):
        """
        Mevcut sıradaki oyuncu nesnesini döndür
        Return: Player object
        """
        if self.current_player == self.player1.symbol:
            return self.player1
        else:
            return self.player2
    
    def restart_game(self):
        """
        Oyunu yeniden başlat (aynı oyuncularla)
        """
        self.game_board.reset()
        self.current_player = "X"  # X her zaman başlar
        self.game_status = Status.STARTED
        self.move_count = 0
        self.winner = None
        print("Oyun yeniden başlatıldı!")
        self.game_board.display()