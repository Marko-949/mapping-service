import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-commerce Mapping Service"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Redis konfiguracija
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data" 
    
    # Celery konfiguracija (izvlačenje u settings)
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL

settings = Settings()

# Kreiranje foldera (ostaje isto, to je ok)
os.makedirs(settings.DATA_DIR, exist_ok=True)