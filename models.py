from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateRoomRequest(BaseModel):
    room_name: str
    password: Optional[str] = None
    username: str
    expire_minutes: int

class JoinRoomRequest(BaseModel):
    room_name: str
    password: Optional[str] = None
    username: str

class MessageRequest(BaseModel):
    room_code: str
    username: str
    content: str

class RoomResponse(BaseModel):
    room_name: str
    users: list[str]
    expire_at: str
    has_password: bool

class CreateRoomResponse(BaseModel):
    room_name: str
