import asyncio
import websockets
import json
import uuid


class GameServer:
    def __init__(self, host = 'localhost', port = 123456):
        self.host = host
        self.port = port 
        self.clients = set()

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        try : 
            async for message in websocket:
                        for client in self.clients:
                            if client != websocket:
                                await client.send(message)           
        except websockets.ConnectionClosed:
            print("client disconnected")
            
        finally:
            self.clients.remove(websocket)
            
    async def start_server(self):
        async with websockets.serve(self.handle_client, 'localhost', 123456) as server :     
            await server.serve_forever()
            
    async def broadcast_game_state(self, game_id):
        pass
    def create_game_room(self):
        pass
    def add_player_to_room(self, player_id, room_id):
        pass
        



class GameRoom:
    def __init__(self, room_id):
        pass
    def add_player(self, websocket, player_info):
        pass
    def remove_player(self, websocket):
        pass
    def is_full(self):
        pass
    def broadcast(self, message):
        pass
    def start_game(self):
        pass
        
        
async def main():
    server = GameServer()
    await server.start_server()

asyncio.run(main())