from pydantic_settings import BaseSettings, SettingsConfigDict

from src.database.config import DBSettings

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    model_config = SettingsConfigDict(env_file=".env")
    
settings = Settings()
