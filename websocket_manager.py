from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_code: str):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = []
        self.active_connections[room_code].append(websocket)

    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.active_connections:
            if websocket in self.active_connections[room_code]:
                self.active_connections[room_code].remove(websocket)

    async def broadcast(self, message: dict, room_code: str, exclude: WebSocket = None):
        if room_code in self.active_connections:
            for connection in self.active_connections[room_code]:
                if connection == exclude:
                    continue
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()
