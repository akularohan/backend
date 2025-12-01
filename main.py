from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo, close_mongo_connection
from routes import rooms, websocket
from contextlib import asynccontextmanager
import asyncio
from cleanup_task import cleanup_expired_rooms

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    asyncio.create_task(cleanup_expired_rooms())
    print("🚀 Background cleanup task started")
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(title="Anonymously API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rooms.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {"message": "Anonymously API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
