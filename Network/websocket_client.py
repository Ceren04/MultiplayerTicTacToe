import asyncio
import websockets
import json
from enum import Enum

class ClientStatus(Enum):
    DISCONNECTED = 1
    CONNECTING = 2
    CONNECTED = 3


class GameClient:
    def __init__(self, server_url=""):
        self.server_url = server_url
        self.websocket = None
        self.status = ClientStatus.DISCONNECTED


    async def connect(self):
        
        try:
            self.status = ClientStatus.CONNECTING
            self.websocket = await websockets.connect(self.server_url)
            self.status = ClientStatus.CONNECTED
            return True
        except Exception:
            self.status = ClientStatus.DISCONNECTED
            return False

    async def disconnect(self):

        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.stats = ClientStatus.DISCONNECTED
        return True 
    
    async def send_message(self, message):
        
        if self.websocket and self.status == ClientStatus.CONNECTED:
            try:
                data = json.dumps(message)
                await self.websocket.send(data)
                return True
            except Exception:
                return False

    async def send_move(self, row, col):
        
        message = {
            "type": "move",
            "row": row,
            "col": col
        }
        return await self.send_message(message)
    

    async def listen_for_updates(self):
        while True : 
            try:
                message = await self.websocket.recv()
                return message
            except self.websocket.ConnectionClosed:
                print("Failure in client")
                break
