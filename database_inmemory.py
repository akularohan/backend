"""In-memory database fallback for development"""
from datetime import datetime
from typing import Dict, List

class InMemoryDatabase:
    def __init__(self):
        self.rooms: Dict = {}
        self.messages: List = []
    
    async def insert_one(self, data):
        if 'code' in data:  # Room
            self.rooms[data['code']] = data
        else:  # Message
            self.messages.append(data)
        return type('obj', (object,), {'inserted_id': 'temp_id'})
    
    async def find_one(self, query):
        if 'code' in query:
            return self.rooms.get(query['code'])
        return None
    
    async def update_one(self, query, update):
        if 'code' in query and query['code'] in self.rooms:
            if '$addToSet' in update:
                for key, value in update['$addToSet'].items():
                    if key not in self.rooms[query['code']]:
                        self.rooms[query['code']][key] = []
                    if value not in self.rooms[query['code']][key]:
                        self.rooms[query['code']][key].append(value)
            if '$pull' in update:
                for key, value in update['$pull'].items():
                    if key in self.rooms[query['code']] and value in self.rooms[query['code']][key]:
                        self.rooms[query['code']][key].remove(value)
        return None
    
    async def delete_one(self, query):
        if 'code' in query and query['code'] in self.rooms:
            del self.rooms[query['code']]
        return None

# Global in-memory collections
rooms_collection = InMemoryDatabase()
messages_collection = InMemoryDatabase()

async def get_database():
    return type('obj', (object,), {
        'rooms': rooms_collection,
        'messages': messages_collection
    })

async def connect_to_mongo():
    print("Using in-memory database (MongoDB connection failed)")

async def close_mongo_connection():
    print("Closed in-memory database")
