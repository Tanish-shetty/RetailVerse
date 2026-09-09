from pathlib import Path
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / '.env'), extra='ignore')
    database_url: str = ''
    etl_database_url: str = ''
    data_source: Literal['csv', 'mysql'] = 'csv'
    groq_api_key: str = ''
    groq_model: str = 'llama-3.3-70b-versatile'
    cors_origins: str = 'http://localhost:5173'


@lru_cache
def settings() -> Settings:
    return Settings()
