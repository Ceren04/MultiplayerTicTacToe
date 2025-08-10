class GameServer:
    def __init__(self, host, port)
    async def start_server(self)
    async def handle_client(self, websocket, path)
    async def broadcast_game_state(self, game_id)
    def create_game_room(self)
    def add_player_to_room(self, player_id, room_id)


class GameRoom:
    def __init__(self, room_id)
    def add_player(self, websocket, player_info)
    def remove_player(self, websocket)
    def is_full(self)
    def broadcast(self, message)
    def start_game(self)