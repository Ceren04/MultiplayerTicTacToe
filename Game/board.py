class GameBoard:
    def __init__(self):
        """
        3x3 boş board oluştur
        Board: 2D list, boş hücreler için None kullan
        """
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.size = 3


    def make_move(self, row, col, player):
        pass

    def is_valid_move(self, row, col):
        pass

    def check_winner(self):
        pass

    def is_board_full(self):
        pass

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

    def get_state(self):
        pass
