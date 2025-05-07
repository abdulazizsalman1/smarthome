from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from . import models
from .database import SessionLocal

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}  # home_id: [websockets]

    async def connect(self, websocket: WebSocket, home_id: int):
        await websocket.accept()
        if home_id not in self.active_connections:
            self.active_connections[home_id] = []
        self.active_connections[home_id].append(websocket)

    def disconnect(self, websocket: WebSocket, home_id: int):
        if home_id in self.active_connections:
            self.active_connections[home_id].remove(websocket)
            if not self.active_connections[home_id]:
                del self.active_connections[home_id]

    async def broadcast(self, home_id: int, message: dict):
        if home_id in self.active_connections:
            for connection in self.active_connections[home_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, home_id)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, home_id: int):
    await manager.connect(websocket, home_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages if needed
            # For now, we'll just echo the message back
            await manager.broadcast(home_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, home_id)

async def notify_device_update(home_id: int, device: models.Device):
    message = {
        "type": "device_update",
        "device_id": device.id,
        "status": device.status,
        "brightness": device.brightness,
        "color": device.color,
        "position": device.position
    }
    await manager.broadcast(home_id, message) 