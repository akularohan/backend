from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from models import CreateRoomRequest, JoinRoomRequest, CreateRoomResponse, RoomResponse
from database import get_database
from utils import generate_room_code

router = APIRouter(prefix="/api", tags=["rooms"])

@router.post("/create-room", response_model=CreateRoomResponse)
async def create_room(request: CreateRoomRequest):
    db = await get_database()
    rooms_collection = db.rooms if hasattr(db, 'rooms') else db["rooms"]
    
    # Check if room exists
    existing_room = await rooms_collection.find_one({"name": request.room_name})
    if existing_room:
        raise HTTPException(status_code=400, detail="Room name already exists")
    
    expire_at = datetime.utcnow() + timedelta(minutes=request.expire_minutes)
    
    room = {
        "name": request.room_name,
        "password": request.password,  # Store password (in production, hash this!)
        "creator": request.username,
        "created_at": datetime.utcnow(),
        "expire_at": expire_at,
        "users": [request.username]
    }
    
    await rooms_collection.insert_one(room)
    return CreateRoomResponse(room_name=request.room_name)

@router.post("/join-room")
async def join_room(request: JoinRoomRequest):
    db = await get_database()
    rooms_collection = db.rooms if hasattr(db, 'rooms') else db["rooms"]
    
    room = await rooms_collection.find_one({"name": request.room_name})
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if datetime.utcnow() > room["expire_at"]:
        await rooms_collection.delete_one({"name": request.room_name})
        raise HTTPException(status_code=410, detail="Room has expired")
    
    # Check password if room has one
    if room.get("password"):
        if not request.password or request.password != room["password"]:
            raise HTTPException(status_code=403, detail="Incorrect password")
    
    # Add user to room
    await rooms_collection.update_one(
        {"name": request.room_name},
        {"$addToSet": {"users": request.username}}
    )
    
    return {"room_name": room["name"], "has_password": bool(room.get("password"))}

@router.get("/room/{room_name}", response_model=RoomResponse)
async def get_room(room_name: str):
    db = await get_database()
    rooms_collection = db.rooms if hasattr(db, 'rooms') else db["rooms"]
    
    room = await rooms_collection.find_one({"name": room_name})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if datetime.utcnow() > room["expire_at"]:
        await rooms_collection.delete_one({"name": room_name})
        raise HTTPException(status_code=410, detail="Room has expired")
    
    return RoomResponse(
        room_name=room["name"],
        users=room.get("users", []),
        expire_at=room["expire_at"].isoformat() + 'Z',
        has_password=bool(room.get("password"))
    )

@router.delete("/leave-room/{room_name}/{username}")
async def leave_room(room_name: str, username: str):
    db = await get_database()
    rooms_collection = db.rooms if hasattr(db, 'rooms') else db["rooms"]
    
    await rooms_collection.update_one(
        {"name": room_name},
        {"$pull": {"users": username}}
    )
    return {"message": "Left room successfully"}
