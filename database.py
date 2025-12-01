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

async def get_database():
    if db.use_inmemory:
        return type('DB', (), {'rooms': inmem_rooms, 'messages': inmem_messages})()
    return db.client[settings.database_name]

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
        await db.client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("📝 Using in-memory storage (data will be lost on restart)")
        db.use_inmemory = True

async def close_mongo_connection():
    if not db.use_inmemory:
        db.client.close()
    print("Closed database connection")
