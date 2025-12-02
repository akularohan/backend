from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings
import certifi

settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    use_inmemory = False
    
db = Database()

# In-memory fallback
class InMemoryCollection:
    def __init__(self):
        self.data = {}
        self.messages = []
    
    async def insert_one(self, doc):
        if 'name' in doc:
            self.data[doc['name']] = doc
        else:
            self.messages.append(doc)
        return type('obj', (object,), {'inserted_id': 'temp'})
    
    async def find_one(self, query):
        if 'name' in query:
            return self.data.get(query['name'])
        return None
    
    def find(self, query):
        # Return async iterator for messages
        class AsyncIterator:
            def __init__(self, items):
                self.items = items
                self.index = 0
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                if self.index >= len(self.items):
                    raise StopAsyncIteration
                item = self.items[self.index]
                self.index += 1
                return item
            
            def sort(self, *args, **kwargs):
                return self
        
        if 'room_name' in query:
            filtered = [m for m in self.messages if m.get('room_name') == query['room_name']]
            return AsyncIterator(filtered)
        return AsyncIterator(list(self.data.values()))
    
    async def count_documents(self, query):
        if 'room_name' in query:
            return len([m for m in self.messages if m.get('room_name') == query['room_name']])
        return len(self.messages)
    
    async def update_one(self, query, update):
        if 'name' in query and query['name'] in self.data:
            if '$addToSet' in update:
                for key, val in update['$addToSet'].items():
                    if key not in self.data[query['name']]:
                        self.data[query['name']][key] = []
                    if val not in self.data[query['name']][key]:
                        self.data[query['name']][key].append(val)
            if '$pull' in update:
                for key, val in update['$pull'].items():
                    if key in self.data[query['name']] and val in self.data[query['name']][key]:
                        self.data[query['name']][key].remove(val)
    
    async def delete_one(self, query):
        if 'name' in query and query['name'] in self.data:
            del self.data[query['name']]

inmem_rooms = InMemoryCollection()
inmem_messages = InMemoryCollection()

class InMemoryDB:
    def __init__(self):
        self.rooms = inmem_rooms
        self.messages = inmem_messages

async def get_database():
    if db.use_inmemory:
        return InMemoryDB()
    return db.client[settings.database_name]

async def connect_to_mongo():
    try:
        if not settings.mongodb_url:
            raise Exception("MONGODB_URL environment variable not set")
        
        print(f"🔌 Attempting to connect to MongoDB...")
        print(f"🔌 Database name: {settings.database_name}")
        print(f"🔌 Connection string starts with: {settings.mongodb_url[:30]}...")
        
        # Try multiple connection methods for better compatibility
        try:
            # Method 1: With certifi
            db.client = AsyncIOMotorClient(
                settings.mongodb_url,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            await db.client.admin.command('ping')
        except Exception as e1:
            print(f"⚠️  Method 1 failed: {e1}")
            print("🔄 Trying alternative connection method...")
            # Method 2: Without certifi, let system handle SSL
            db.client = AsyncIOMotorClient(
                settings.mongodb_url,
                tls=True,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            await db.client.admin.command('ping')
        
        print("✅ Connected to MongoDB successfully!")
        db.use_inmemory = False
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("📝 Using in-memory storage (data will be lost on restart)")
        db.use_inmemory = True

async def close_mongo_connection():
    if not db.use_inmemory:
        db.client.close()
    print("Closed database connection")
