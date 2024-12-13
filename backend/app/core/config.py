from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        self.PROJECT_NAME: str = "SonicWall API"
        self.API_V1_STR: str = "/api/v1"
        
        # API Settings
        self.API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(os.getenv("API_PORT", "8000"))
        
        # Database
        self.POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
        self.POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.POSTGRES_DB: str = os.getenv("POSTGRES_DB", "sonicwall")
        self.SQLALCHEMY_DATABASE_URI: str = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        
        # Security
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
        
        # SSL/TLS Settings
        self.SSL_KEYFILE: str = os.getenv("SSL_KEYFILE", "")
        self.SSL_CERTFILE: str = os.getenv("SSL_CERTFILE", "")
        
        # CORS
        self.ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
        
        # Debug
        self.SQL_DEBUG: bool = os.getenv("SQL_DEBUG", "false").lower() == "true"

        # SonicWall Configuration
        self.SONICWALL_HOST: str = os.getenv("SONICWALL_HOST", "")
        self.SONICWALL_PORT: int = int(os.getenv("SONICWALL_PORT", "443"))
        self.SONICWALL_USERNAME: str = os.getenv("SONICWALL_USERNAME", "")
        self.SONICWALL_PASSWORD: str = os.getenv("SONICWALL_PASSWORD", "")
        self.SONICWALL_VERIFY_SSL: bool = os.getenv("SONICWALL_VERIFY_SSL", "false").lower() == "true"
        self.SONICWALL_API_VERSION: str = os.getenv("SONICWALL_API_VERSION", "7.0")

    @property
    def CORS_ORIGINS(self) -> list:
        return self.ALLOWED_ORIGINS.split(",")

settings = Settings() 