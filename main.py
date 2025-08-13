import asyncio
import sys
import os
from UI.terminal_ui import TerminalUI
from Network.websocket_server import GameServer
from Network.websocket_client import GameClient
from Game.player import Player
from Game.game_logic import Game
from Utils.validator import GameValidator

class TicTacToeApp:
    """
    Ana uygulama sınıfı - Tüm modları yönetir
    WebSocket Host/Client ve P2P Host/Client modları
    """
    
    def __init__(self):
        """
        Uygulama state'ini initialize et
        UI component'lerini hazırla
        """
        self.ui = TerminalUI()
        self.running = True
        self.current_mode = None
        
    def show_main_menu(self):
        """
        Ana menüyü göster ve kullanıcı seçimini al
        Return: kullanıcının seçimi (string)
        """
        while self.running:
            choice = self.ui.display_menu()
            
            if choice == "1":
                asyncio.run(self.start_host_mode())
            elif choice == "2":
                asyncio.run(self.start_client_mode())
            elif choice == "3":
                self.start_p2p_host()
            elif choice == "4":
                self.start_p2p_client()
            elif choice == "5":
                self.ui.show_info("Çıkılıyor... Görüşürüz!")
                self.running = False
                break
            else:
                self.ui.show_error("Geçersiz seçim!")
    
    async def start_host_mode(self):
        """
        WebSocket server mode'u başlat
        Server'ı ayaklandır, port bilgisini göster
        """
        try:
            self.ui.show_info("WebSocket Host modunda başlatılıyor...")
            
            # Server bilgilerini al
            host, port = self.ui.get_server_info()
            
            # Bağlantı parametrelerini validate et
            valid, error = GameValidator.validate_connection_params(host, port)
            if not valid:
                self.ui.show_error(f"Bağlantı hatası: {error}")
                return
            
            # Server'ı başlat
            server = GameServer(host, port)
            self.ui.show_server_started(host, port)
            
            # Server'ı çalıştır
            await server.start_server()
            
        except KeyboardInterrupt:
            self.ui.show_info("Server kapatılıyor...")
        except Exception as e:
            self.ui.show_error(f"Server hatası: {e}")
    
    async def start_client_mode(self):
        """
        Client mode başlat
        Server IP/port al, bağlantı kur
        """
        try:
            self.ui.show_info("WebSocket Client modunda başlatılıyor...")
            
            # Server bilgilerini al
            host, port = self.ui.get_server_info()
            
            # Bağlantı parametrelerini validate et
            valid, error = GameValidator.validate_connection_params(host, port)
            if not valid:
                self.ui.show_error(f"Bağlantı hatası: {error}")
                return
            
            # Server URL oluştur
            server_url = f"ws://{host}:{port}"
            
            # Client oluştur ve bağlan
            client = GameClient(server_url)
            self.ui.show_connection_status("connecting")
            
            # Bağlantıyı dene
            if await client.connect():
                self.ui.show_connection_status("connected")
                self.ui.show_info("Server'a başarıyla bağlanıldı!")
                
                # Oyuncu bilgilerini al
                player_name = input("Adınızı girin: ").strip()
                if not player_name:
                    player_name = "Oyuncu"
                
                # Client oyun loop'unu başlat
                await self.client_game_loop(client, player_name)
                
            else:
                self.ui.show_connection_status("error")
                self.ui.show_error("Server'a bağlanılamadı!")
                
        except KeyboardInterrupt:
            self.ui.show_info("Client kapatılıyor...")
            if 'client' in locals():
                await client.disconnect()
        except Exception as e:
            self.ui.show_error(f"Client hatası: {e}")
    
    async def client_game_loop(self, client, player_name):
        """
        Client tarafında oyun döngüsü
        
        Args:
            client (GameClient): WebSocket client
            player_name (str): Oyuncu adı
        """
        try:
            # Oyuncu oluştur (symbol server tarafından atanacak)
            player = Player(player_id=1, symbol="X", name=player_name)
            
            self.ui.show_info("Oyuncu bekleniyor...")
            
            # Game loop
            while True:
                # Server'dan mesaj bekle
                message = await client.listen_for_updates()
                if not message:
                    break
                
                # Mesajı parse et
                from protocol import GameProtocol
                parsed_message = GameProtocol.deserialize_message(message)
                
                if not parsed_message:
                    continue
                
                message_type = parsed_message.get("type")
                
                if message_type == "game_state":
                    # Game state güncellendi
                    game_data = GameProtocol.extract_game_state_data(parsed_message)
                    if game_data:
                        self.handle_game_state_update(game_data, player, client)
                
                elif message_type == "game_start":
                    # Oyun başladı
                    self.ui.show_info("Oyun başlıyor!")
                    data = parsed_message.get("data", {})
                    # Player symbol'unu güncelle
                    for p in data.get("players", []):
                        if p.get("name") == player_name:
                            player.symbol = p.get("symbol")
                            break
                
                elif message_type == "game_end":
                    # Oyun bitti
                    data = parsed_message.get("data", {})
                    winner = data.get("winner")
                    self.ui.show_winner(winner)
                    break
                
                elif message_type == "error":
                    # Hata mesajı
                    data = parsed_message.get("data", {})
                    self.ui.show_error(data.get("message", "Bilinmeyen hata"))
                
        except Exception as e:
            self.ui.show_error(f"Oyun loop hatası: {e}")
    
    def handle_game_state_update(self, game_data, player, client):
        """
        Game state güncellemelerini handle et
        
        Args:
            game_data (dict): Oyun durumu verisi
            player (Player): Local player
            client (GameClient): WebSocket client
        """
        try:
            # Board'u göster
            board = game_data.get("board", [])
            self.ui.display_board(board)
            
            # Sıra bilgisini göster
            current_player = game_data.get("current_player")
            is_my_turn = player.is_turn(current_player)
            self.ui.show_turn_info(current_player, is_my_turn)
            
            # Eğer bizim sıramızsa hamle al
            if is_my_turn and not game_data.get("is_game_over", False):
                move = self.ui.get_move_input()
                if move:
                    row, col = move
                    # Hamleyi server'a gönder
                    asyncio.create_task(client.send_move(player, row, col))
                    
        except Exception as e:
            self.ui.show_error(f"Game state update hatası: {e}")
    
    
    def start_local_game(self):
        """
        Local 2 player oyunu başlat (test için)
        """
        try:
            self.ui.show_info("Local oyun başlatılıyor...")
            
            # Oyuncuları oluştur
            player1_name = input("Oyuncu 1 adı (X): ").strip() or "Oyuncu 1"
            player2_name = input("Oyuncu 2 adı (O): ").strip() or "Oyuncu 2"
            
            player1 = Player(player_id=1, symbol="X", name=player1_name)
            player2 = Player(player_id=2, symbol="O", name=player2_name)
            
            # Oyunu başlat
            game = Game(player1, player2)
            game.start_game()
            
            # Oyun döngüsü
            while game.game_status.name == "STARTED":
                current_player_obj = game.get_current_player_object()
                
                self.ui.show_turn_info(game.current_player, True)
                
                # Hamle al
                move = current_player_obj.get_move()
                if move:
                    row, col = move
                    
                    # Hamleyi işle
                    success, message, game_state = game.process_move(current_player_obj, row, col)
                    
                    if success:
                        self.ui.show_info(message)
                        self.ui.display_board(game_state["board"])
                        
                        if game_state.get("is_game_over"):
                            break
                    else:
                        self.ui.show_error(message)
            
            # Oyun sonucu
            game.end_game()
            
        except KeyboardInterrupt:
            self.ui.show_info("Oyun iptal edildi.")
        except Exception as e:
            self.ui.show_error(f"Local oyun hatası: {e}")
    
    def run(self):
        """
        Ana application loop'u
        Menu selection handle et, ilgili mode'ları başlat
        """
        try:
            self.ui.show_info("Tic-Tac-Toe Multiplayer'a Hoş Geldiniz!")
            self.show_main_menu()
            
        except KeyboardInterrupt:
            self.ui.show_info("\nUygulama kapatılıyor...")
        except Exception as e:
            self.ui.show_error(f"Uygulama hatası: {e}")
        finally:
            self.ui.show_info("Görüşürüz!")


def main():
    """
    Uygulama entry point'i
    """
    app = TicTacToeApp()
    app.run()


if __name__ == "__main__":
    main()