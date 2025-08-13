from board import GameBoard
from enum import Enum

class Status(Enum):
    FINISHED = 1
    STARTED = 2
    

class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.game_board = GameBoard()
        self.current_player = self.player1
        self.game_status = Status.STARTED
        
    def start_game(self):
        
        print("---------------------------TicTacToe---------------------------------")
        
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
            
            Örnek:
            success, msg, state = game.process_move(player1, 1, 1)
            if success:
                print(f"Hamle başarılı: {msg}")
                # Network'e state'i broadcast et
            else:
                print(f"Hata: {msg}")
        """
        if player.is_turn(self.current_player):
            if self.game_board.is_valid_move():
                self.game_board.make_move(row,col,player)
                if self.game_board.check_winner():
                    self.game_status = Status.FINISHED
                
                return (True, f"{player} hamlesini yaptı",self.game_board.board)
            
    def switch_turn(self):
        """
        Sırayı diğer oyuncuya geçir
        
        Logic:
        - Eğer current_player == player1 ise -> player2'ye geçir
        - Eğer current_player == player2 ise -> player1'e geçir
        
        Kullanım:
        - Her başarılı hamle sonrası çağrılır
        - Multiplayer'da critical: sıra takibi için
        """
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1
            return self.current_player
    def end_game(self):
        
    def get_game_state(self):