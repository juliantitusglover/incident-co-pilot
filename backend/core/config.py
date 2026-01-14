from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings, case_sensitive=True):
    APP_ENV: str = "local"
    LOG_LEVEL: str = "info"

    API_TITLE: str = "Incident Co-Pilot API"
    API_DESCRIPTION: str = "Incident Co-Pilot is a lightweight incident timeline capture and summarisation tool."
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    CORS_ORIGINS: str = ""

    DEBUG: bool = False

    OPENAI_API_KEY: str

    @field_validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings():
    return Settings()