import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    chroma_db_path: str = "./data/chroma_db"
    upload_dir: str = "./data/documents"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens: int = 4000
    temperature: float = 0.7
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
Path(settings.chroma_db_path).mkdir(parents=True, exist_ok=True)
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)