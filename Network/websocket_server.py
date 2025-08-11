import asyncio
import websockets
import json
import uuid
from enum import Enum


class Status(Enum):
    WAITING = 1
    IN_PROGRESS = 2
    FINISHED = 3

    
    
class GameServer:
    def __init__(self, host = 'localhost', port = 123456):
        self.host = host
        self.port = port 
        self.clients = set()
        self.game_rooms = {} # {room_id : GameRoom}
        
    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        try : 
            async for message in websocket:
                pass
        except websocket.ConnectionClosed:
            print("Client disconnected")
        finally:
            self.clients.remove(websocket)
            
    async def start_server(self):
        async with websockets.serve(self.handle_client, self.host, self.port) as server :     
            await server.Future()
            
    def create_game_room(self):
        gameroom = GameRoom()
        self.game_rooms[gameroom.room_id] = gameroom
        return gameroom
    
    def add_player_to_room(self, websocket, player_info, room_id):
        gameroom = self.gamerooms[room_id]
        if gameroom.add_player(websocket,player_info):
            return True
        return False
        


class GameRoom:
    room_counter = 0  # Static variable for unique room IDs

    def __init__(self, max_players=2):
        GameRoom.room_counter += 1
        self.room_id = GameRoom.room_counter  # Unique ID
        self.max_players = max_players
        self.status = Status.WAITING
        self.game_state = {}
        self.players = []  # list of dicts: {"websocket": ws, "player_info": {...}}

    def add_player(self, websocket, player_info):
        if websocket and player_info and not self.is_full():
            self.players.append({
                "websocket": websocket,
                "player_info": player_info
            })
            return True
        return False

    def remove_player(self, websocket):
        if websocket:
            for player in self.players:
                if player["websocket"] == websocket:
                    self.players.remove(player)
                    return True
        return False

    def is_full(self):
        return len(self.players) >= self.max_players

    async def broadcast(self, message, exclude_ws=None):
        """Broadcast message to all players except optionally one websocket."""
        if not self.players:
            return

        data = json.dumps(message)

        websockets_to_send = [
            player["websocket"]
            for player in self.players
            if player["websocket"] != exclude_ws
        ]

        if websockets_to_send:
            await asyncio.gather(
                *(ws.send(data) for ws in websockets_to_send),
                return_exceptions=True
            )

    def start_game(self, board, status):
        self.status = Status.IN_PROGRESS
        self.game_state = {"board": board, "status": status}

    async def update_game_state(self, new_state):
        self.game_state = new_state
        await self.broadcast(message=new_state)  # Await because broadcast is async
        
        
async def main():
    server = GameServer()
    await server.start_server()

asyncio.run(main())