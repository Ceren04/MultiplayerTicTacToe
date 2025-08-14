class GameValidator:
    """
    Tic-Tac-Toe oyunu için validation fonksiyonları
    Input validation, move validation, game state validation
    """
    
    @staticmethod
    def validate_move(board, row, col):
        """
        Hamlenin board'da geçerli olup olmadığını comprehensive kontrol et
        
        Args:
            board (list): 3x3 board matrix
            row (int): Satır koordinatı
            col (int): Sütun koordinatı
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        # Koordinat validation
        coord_valid, coord_error = GameValidator.validate_coordinates(row, col)
        if not coord_valid:
            return False, coord_error
        
        # Board None kontrolü
        if board is None:
            return False, "Board tanımlanmamış!"
        
        # Board boyut kontrolü
        if len(board) != 3:
            return False, "Board 3x3 olmalı!"
        
        for board_row in board:
            if not isinstance(board_row, list) or len(board_row) != 3:
                return False, "Board satırları 3 elemanlı list olmalı!"
        
        # Hücre boş mu kontrolü
        try:
            if board[row][col] is not None:
                return False, f"Pozisyon ({row},{col}) zaten dolu!"
        except IndexError:
            return False, f"Koordinat ({row},{col}) board dışında!"
        
        return True, "Hamle geçerli"
    
    @staticmethod
    def validate_coordinates(row, col):
        """
        Koordinatların 0-2 arasında ve geçerli tipte olup olmadığını kontrol et
        
        Args:
            row (any): Satır koordinatı
            col (any): Sütun koordinatı
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        # Type kontrolü
        if not isinstance(row, int):
            return False, f"Satır koordinatı integer olmalı! Girilen: {type(row).__name__}"
        
        if not isinstance(col, int):
            return False, f"Sütun koordinatı integer olmalı! Girilen: {type(col).__name__}"
        
        # Range kontrolü
        if not (0 <= row <= 2):
            return False, f"Satır koordinatı 0-2 arasında olmalı! Girilen: {row}"
        
        if not (0 <= col <= 2):
            return False, f"Sütun koordinatı 0-2 arasında olmalı! Girilen: {col}"
        
        return True, "Koordinatlar geçerli"
    
    @staticmethod
    def validate_player_symbol(symbol):
        """
        Oyuncu sembolünün geçerliliğini kontrol et
        
        Args:
            symbol (any): Kontrol edilecek sembol
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not isinstance(symbol, str):
            return False, f"Sembol string olmalı! Girilen: {type(symbol).__name__}"
        
        if symbol not in ["X", "O"]:
            return False, f"Sembol 'X' veya 'O' olmalı! Girilen: {symbol}"
        
        return True, "Sembol geçerli"
    
    @staticmethod
    def validate_player_data(player_data):
        """
        Oyuncu verilerinin geçerliliğini kontrol et
        
        Args:
            player_data (dict): Oyuncu bilgileri
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not isinstance(player_data, dict):
            return False, "Oyuncu verisi dict formatında olmalı!"
        
        # Gerekli field'lar
        required_fields = ["id", "symbol", "name"]
        missing_fields = [field for field in required_fields if field not in player_data]
        
        if missing_fields:
            return False, f"Eksik alanlar: {', '.join(missing_fields)}"
        
        # Player ID kontrolü
        player_id = player_data.get("id")
        if not isinstance(player_id, (str, int)) or str(player_id).strip() == "":
            return False, "Player ID geçerli bir string/int olmalı!"
        
        # Sembol kontrolü
        symbol_valid, symbol_error = GameValidator.validate_player_symbol(player_data.get("symbol"))
        if not symbol_valid:
            return False, symbol_error
        
        # İsim kontrolü
        name = player_data.get("name")
        if not isinstance(name, str) or name.strip() == "":
            return False, "Player name geçerli bir string olmalı!"
        
        if len(name.strip()) > 20:
            return False, "Player name 20 karakterden uzun olamaz!"
        
        return True, "Oyuncu verisi geçerli"
    
    @staticmethod
    def validate_board_state(board):
        """
        Board durumunun geçerliliğini comprehensive kontrol et
        
        Args:
            board (list): 3x3 board matrix
            
        Returns:
            tuple: (is_valid: bool, error_message: str, analysis: dict)
        """
        if not isinstance(board, list):
            return False, "Board list formatında olmalı!", {}
        
        if len(board) != 3:
            return False, "Board 3 satır içermeli!", {}
        
        # Board analizi
        x_count = 0
        o_count = 0
        empty_count = 0
        
        for row_idx, row in enumerate(board):
            if not isinstance(row, list):
                return False, f"Satır {row_idx} list formatında olmalı!", {}
            
            if len(row) != 3:
                return False, f"Satır {row_idx} 3 element içermeli!", {}
            
            for col_idx, cell in enumerate(row):
                if cell is None:
                    empty_count += 1
                elif cell == "X":
                    x_count += 1
                elif cell == "O":
                    o_count += 1
                else:
                    return False, f"Geçersiz cell değeri ({row_idx},{col_idx}): {cell}. Sadece None, 'X', 'O' olabilir!", {}
        
        # Hamle sayısı mantık kontrolü
        if x_count < o_count or x_count > o_count + 1:
            return False, f"Geçersiz hamle dağılımı! X: {x_count}, O: {o_count}. X önce başlar ve en fazla 1 fazla olabilir!", {}
        
        analysis = {
            "x_count": x_count,
            "o_count": o_count,
            "empty_count": empty_count,
            "total_moves": x_count + o_count,
            "game_stage": "early" if x_count + o_count < 3 else "mid" if x_count + o_count < 6 else "late"
        }
        
        return True, "Board durumu geçerli", analysis
    
    @staticmethod
    def validate_game_state(game_state):
        """
        Oyun durumunun geçerliliğini kontrol et
        
        Args:
            game_state (dict): Oyun durumu verisi
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not isinstance(game_state, dict):
            return False, "Game state dict formatında olmalı!"
        
        # Gerekli field'lar
        required_fields = ["board", "current_player", "game_status"]
        missing_fields = [field for field in required_fields if field not in game_state]
        
        if missing_fields:
            return False, f"Eksik alanlar: {', '.join(missing_fields)}"
        
        # Board kontrolü
        board_valid, board_error, _ = GameValidator.validate_board_state(game_state.get("board"))
        if not board_valid:
            return False, f"Board hatası: {board_error}"
        
        # Current player kontrolü
        current_player = game_state.get("current_player")
        player_valid, player_error = GameValidator.validate_player_symbol(current_player)
        if not player_valid:
            return False, f"Current player hatası: {player_error}"
        
        # Game status kontrolü
        game_status = game_state.get("game_status")
        valid_statuses = ["STARTED", "FINISHED", "WAITING"]
        if game_status not in valid_statuses:
            return False, f"Geçersiz game status: {game_status}. Geçerli değerler: {valid_statuses}"
        
        return True, "Game state geçerli"
    
    @staticmethod
    def validate_network_message(message):
        """
        Network mesajının geçerliliğini kontrol et
        
        Args:
            message (dict): Network mesajı
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not isinstance(message, dict):
            return False, "Mesaj dict formatında olmalı!"
        
        # Type field kontrolü
        if "type" not in message:
            return False, "Mesaj 'type' field'ı içermeli!"
        
        message_type = message.get("type")
        if not isinstance(message_type, str) or message_type.strip() == "":
            return False, "Message type geçerli bir string olmalı!"
        
        # Data field kontrolü
        if "data" not in message:
            return False, "Mesaj 'data' field'ı içermeli!"
        
        if not isinstance(message.get("data"), dict):
            return False, "Data field dict formatında olmalı!"
        
        # Timestamp kontrolü (opsiyonel)
        if "timestamp" in message:
            timestamp = message.get("timestamp")
            if not isinstance(timestamp, (int, float)) or timestamp <= 0:
                return False, "Timestamp geçerli bir sayı olmalı!"
        
        return True, "Network mesajı geçerli"
    
    @staticmethod
    def validate_connection_params(host, port):
        """
        Bağlantı parametrelerinin geçerliliğini kontrol et
        
        Args:
            host (str): Server IP/hostname
            port (int): Port numarası
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        # Host kontrolü
        if not isinstance(host, str) or host.strip() == "":
            return False, "Host geçerli bir string olmalı!"
        
        # Port kontrolü
        if not isinstance(port, int):
            return False, "Port integer olmalı!"
        
        if not (1 <= port <= 65535):
            return False, "Port 1-65535 arasında olmalı!"
        
        # Well-known port uyarısı
        if port < 1024:
            return False, "Port 1024'ten küçük olamaz (system reserved)!"
        
        return True, "Bağlantı parametreleri geçerli"