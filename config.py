from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    mongodb_url: str
    database_name: str = "anonymously"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
