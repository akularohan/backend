from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
from websocket_manager import manager
from database import get_database

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, username: str):
    db = await get_database()
    messages_collection = db.messages if hasattr(db, 'messages') else db["messages"]
    
    await manager.connect(websocket, room_name)
    
    # Notify others that user joined
    await manager.broadcast({
        "type": "user_joined",
        "username": username,
        "timestamp": datetime.utcnow().isoformat()
    }, room_name)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get("type", "text")
            message = {
                "type": "message",
                "message_type": message_type,
                "username": username,
                "content": data["content"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Save message to database
            await messages_collection.insert_one({
                "room_name": room_name,
                "username": username,
                "message_type": message_type,
                "content": data["content"],
                "timestamp": datetime.utcnow()
            })
            
            # Broadcast to all users in room
            await manager.broadcast(message, room_name)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_name)
        await manager.broadcast({
            "type": "user_left",
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }, room_name)
