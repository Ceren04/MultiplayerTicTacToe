class GameBoard:
    def __init__(self):
        """
        3x3 boş board oluştur
        Board: 2D list, boş hücreler için None kullan
        """
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.size = 3
        self.products = [[2,3,5],[7,11,13],[17,19,23]]
        self.winning_patterns = [30,1001,7429,238,627,1495,506,935]
        self.player_product = {
            "X": 1,
            "O": 1
            }
        

    def make_move(self, row, col, player):
        move_validation = self.is_valid_move(row, col)

        if move_validation:
            self.board[row][col] = player
            self.player_product[player] *= self.products[row][col]
            return True
        else:
            return False

    def is_valid_move(self, row, col):
        if (row <= 2 and row >= 0) and (col <= 2 and col >= 0):
            if self.board[row][col] is None :
                return True
        else:
            return False
        
    def check_winner(self):
        """
            Winning patterns : 
            Satırlar: (0,1,2), (3,4,5), (6,7,8)

            Sütunlar: (0,3,6), (1,4,7), (2,5,8)

            Çaprazlar: (0,4,8), (2,4,6) 
        """
        for winning_pattern in self.winning_patterns:
            if self.player_product["X"] % winning_pattern:
                return {"state" : True, "player" : "X" }
            if self.player_product["O"] % winning_pattern:
                return {"state" : True, "player" : "O" }
        return {"state" : False}
        

    def is_board_full(self):
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == None:
                    return False
        return True

    def display(self):
        """
        Board'u terminal'de ASCII art olarak göster
        Koordinat numaraları ile birlikte
        """
        print("\n   0   1   2")  # Sütun numaraları
        print("  -----------")
        
        for row_idx in range(self.size):
            print(f"{row_idx}|", end="")  # Satır numarası
            
            for col_idx in range(self.size):
                # Hücre içeriği
                cell = self.board[row_idx][col_idx]
                if cell is None:
                    display_char = " "
                else:
                    display_char = cell
                
                print(f" {display_char} ", end="")
                
                # Sütun ayırıcısı
                if col_idx < self.size - 1:
                    print("|", end="")
            
            print()  # Satır sonu
            
            # Satır ayırıcısı (son satır değilse)
            if row_idx < self.size - 1:
                print("  -----------")
        
        print("  -----------\n")

    def reset(self):
        """
        Board'u başlangıç durumuna sıfırla
        Tüm hücreleri None yap
        """
        self.board = [[None for _ in range(3)] for _ in range(3)]
        print("Board sıfırlandı!")


