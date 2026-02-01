import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./agency_tracker.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MAX_FAILED_ATTEMPTS: int = 3
    LOCKOUT_DURATION_MINUTES: int = 15
    REQUIRED_SECURITY_COUNTRIES: int = 5
    MIN_CORRECT_COUNTRIES_FOR_RECOVERY: int = 3

    THRESHOLD_GREEN: int = 100
    THRESHOLD_YELLOW: int = 90

    DEV_MODE: bool = os.getenv("DEV_MODE", "true").lower() == "true"
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
