from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGODB_URL", "")
    database_name: str = os.getenv("DATABASE_NAME", "anonymously")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
