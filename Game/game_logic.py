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
        pass
    def switch_turn(self):

        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1
            return self.current_player
        

    def end_game(self):
        
    def get_game_state(self):