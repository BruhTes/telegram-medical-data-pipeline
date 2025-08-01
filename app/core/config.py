"""
Configuration settings for the Telegram Medical Data Pipeline
"""
import os
from typing import Optional
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/telegram_medical")
    postgres_db: str = os.getenv("POSTGRES_DB", "telegram_medical")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "password")
    
    # Telegram settings
    telegram_api_id: Optional[str] = os.getenv("TELEGRAM_API_ID")
    telegram_api_hash: Optional[str] = os.getenv("TELEGRAM_API_HASH")
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_phone: Optional[str] = os.getenv("TELEGRAM_PHONE")
    
    # Application settings
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # dbt settings
    dbt_project_dir: str = os.getenv("DBT_PROJECT_DIR", "/app/dbt")
    dbt_profiles_dir: str = os.getenv("DBT_PROFILES_DIR", "/app/dbt")
    
    # Dagster settings
    dagster_home: str = os.getenv("DAGSTER_HOME", "/app/dagster")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings() 