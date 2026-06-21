"""Application Configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    db_host: str = "localhost"
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "waffledom_db"
    db_port: int = 3306
    
    # Application
    app_name: str = "Waffledom Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
