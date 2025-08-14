class Player:
    def __init__(self, player_id, symbol, name):
        self.player_id = player_id
        self.symbol = symbol
        self.name = name

    def get_move(self):

        while True: 
            move = input("hamlenizi yapınız: 'satır, sütun' şeklinde")
            try:
                move = move.strip()
                
                if not move:
                    print("lütfen bir değer girin!")
                    continue

                parts = move.split(",")

                if len(parts) != 2:
                    print("lütfen 2 değer girin!")
                
                row = int(parts[0])
                col = int(parts[1])

                return (row, col)

            except ValueError:
                print("sayı giriniz!")

    def is_turn(self, current_player):
        
        return current_player == self.symbol

