import os
import sys

class TerminalUI:
    def __init__(self):
        """
        Terminal UI ayarlarını initialize et
        """
        self.menu_options = {
            "1": "WebSocket Host Ol",
            "2": "WebSocket Oyuna Katıl", 
            "3": "P2P Host Ol",
            "4": "P2P Oyuna Katıl",
            "5": "Çıkış"
        }
        
    def display_menu(self):
        """
        Ana menüyü göster ve kullanıcı seçimini al
        Return: kullanıcının seçimi (string)
        """
        self.clear_screen()
        print("=" * 50)
        print("         TIC-TAC-TOE MULTIPLAYER")
        print("=" * 50)
        print()
        
        for key, value in self.menu_options.items():
            print(f"{key}. {value}")
        
        print()
        while True:
            choice = input("Seçiminizi yapın (1-5): ").strip()
            if choice in self.menu_options:
                return choice
            else:
                print("Geçersiz seçim! Lütfen 1-5 arası bir sayı girin.")
    
    def display_board(self, board):
        """
        3x3 board'u terminal'de görsel olarak göster
        board: 2D list [[None, 'X', 'O'], ...]
        """
        print("\n   0   1   2")  # Sütun numaraları
        print("  -----------")
        
        for row_idx in range(3):
            print(f"{row_idx}|", end="")  # Satır numarası
            
            for col_idx in range(3):
                # Hücre içeriği
                cell = board[row_idx][col_idx]
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
    
    def get_move_input(self):
        """
        Kullanıcıdan hamle koordinatlarını al
        Return: (row, col) tuple veya None (quit için)
        """
        while True:
            move_input = input("Hamlenizi girin (satır,sütun) veya 'q' (çıkış): ").strip()
            
            if move_input.lower() == 'q':
                return None
            
            try:
                if ',' not in move_input:
                    print("Lütfen virgülle ayırarak girin! (örnek: 1,2)")
                    continue
                
                parts = move_input.split(',')
                if len(parts) != 2:
                    print("Tam iki değer girin! (örnek: 1,2)")
                    continue
                
                row = int(parts[0].strip())
                col = int(parts[1].strip())
                
                if not (0 <= row <= 2 and 0 <= col <= 2):
                    print("Koordinatlar 0-2 arasında olmalı!")
                    continue
                
                return (row, col)
                
            except ValueError:
                print("Geçerli sayılar girin!")
    
    def show_winner(self, winner):
        """
        Kazanan oyuncuyu göster veya berabere durumunu
        winner: 'X', 'O', 'tie', veya None
        """
        self.clear_screen()
        print("=" * 50)
        
        if winner == 'tie':
            print("           🤝 BERABERE! 🤝")
            print("         İyi oyun, her iki taraf!")
        elif winner:
            print(f"          🎉 {winner} KAZANDI! 🎉")
            print(f"        Tebrikler {winner} oyuncusu!")
        else:
            print("           ❌ OYUN İPTAL ❌")
        
        print("=" * 50)
        input("\nDevam etmek için Enter'a basın...")
    
    def show_connection_status(self, status):
        """
        Network bağlantı durumunu göster
        status: 'connected', 'disconnected', 'connecting', 'waiting'
        """
        status_messages = {
            'connected': "✅ Bağlı",
            'disconnected': "❌ Bağlantı Kesildi",
            'connecting': "🔄 Bağlanıyor...",
            'waiting': "⏳ Oyuncu Bekleniyor...",
            'error': "⚠️ Bağlantı Hatası"
        }
        
        message = status_messages.get(status, f"Durum: {status}")
        print(f"\n[Bağlantı Durumu: {message}]")
    
    def clear_screen(self):
        """
        Terminal ekranını temizle (cross-platform)
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_waiting_for_player(self):
        """
        Oyuncu beklerken gösterilecek mesaj
        """
        print("\n" + "="*40)
        print("  🎮 İkinci oyuncuyu bekliyoruz...")
        print("     Lütfen sabırla bekleyin!")
        print("="*40)
    
    def show_game_info(self, player_symbol, opponent_symbol):
        """
        Oyun başında oyuncu bilgilerini göster
        """
        print(f"\n🎯 Siz: {player_symbol}")
        print(f"🎯 Rakip: {opponent_symbol}")
        print("-" * 30)
    
    def show_turn_info(self, current_player, is_my_turn):
        """
        Kimin sırası olduğunu göster
        """
        if is_my_turn:
            print(f"\n🎯 SİZİN SIRANIZ! ({current_player})")
        else:
            print(f"\n⏳ Rakibin sırası... ({current_player})")
    
    def show_error(self, error_message):
        """
        Hata mesajlarını formatla ve göster
        """
        print(f"\n❌ HATA: {error_message}")
    
    def show_info(self, info_message):
        """
        Bilgi mesajlarını formatla ve göster
        """
        print(f"\nℹ️  {info_message}")
    
    def get_server_info(self):
        """
        Server bağlantı bilgilerini kullanıcıdan al
        Return: (host, port) tuple
        """
        print("\n📡 Server Bağlantı Bilgileri:")
        
        host = input("Server IP (Enter = localhost): ").strip()
        if not host:
            host = "localhost"
        
        while True:
            port_input = input("Port (Enter = 8765): ").strip()
            if not port_input:
                port = 8765
                break
            try:
                port = int(port_input)
                if 1024 <= port <= 65535:
                    break
                else:
                    print("Port 1024-65535 arasında olmalı!")
            except ValueError:
                print("Geçerli bir port numarası girin!")
        
        return host, port
    
    def show_server_started(self, host, port):
        """
        Server başlatıldığında gösterilecek bilgi
        """
        print(f"\n🚀 Server başlatıldı!")
        print(f"📍 Adres: {host}:{port}")
        print("👥 Oyuncular bekleniyor...")
        print("❌ Çıkış için Ctrl+C")
        print("-" * 40)