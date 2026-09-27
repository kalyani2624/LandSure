import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str = "sqlite:///./land_records.db"
    SECRET_KEY: str = "sih_super_secret_jwt_key_2026_land_digitization"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Upload and Preprocessed Directories
    UPLOAD_DIR: str = "uploads"
    PREPROCESSED_DIR: str = "preprocessed"
    
    # External OCR Space fallback API Key
    OCR_SPACE_API_KEY: str = "helloworld"

    # Optional Multimodal Cloud AI Provider (Groq)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.2-11b-vision-preview"

settings = Settings()

# Ensure directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.PREPROCESSED_DIR).mkdir(parents=True, exist_ok=True)
