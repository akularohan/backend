import asyncio
from datetime import datetime
from database import get_database, db

async def cleanup_expired_rooms():
    """Background task to clean up expired rooms"""
    while True:
        try:
            database = await get_database()
            current_time = datetime.utcnow()
            expired_rooms = []
            
            # Check if using in-memory storage
            if db.use_inmemory:
                # In-memory cleanup
                rooms_collection = database.rooms
                if hasattr(rooms_collection, 'data'):
                    for name, room in list(rooms_collection.data.items()):
                        if room.get('expire_at') and current_time > room['expire_at']:
                            expired_rooms.append(name)
                            del rooms_collection.data[name]
            else:
                # MongoDB cleanup
                rooms_collection = database["rooms"]
                messages_collection = database["messages"]
                
                # Find expired rooms
                cursor = rooms_collection.find({"expire_at": {"$lt": current_time}})
                async for room in cursor:
                    expired_rooms.append(room['name'])
                
                # Delete expired rooms and their messages
                if expired_rooms:
                    await rooms_collection.delete_many({"name": {"$in": expired_rooms}})
                    await messages_collection.delete_many({"room_name": {"$in": expired_rooms}})
            
            if expired_rooms:
                print(f"🧹 Cleaned up {len(expired_rooms)} expired rooms: {expired_rooms}")
            
        except Exception as e:
            print(f"⚠️  Cleanup task error: {e}")
        
        # Run every 60 seconds
        await asyncio.sleep(60)
