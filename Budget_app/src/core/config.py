from pydantic_settings import BaseSettings, SettingsConfigDict

from src.database.config import DBSettings
from src.auth.config import AuthSettings

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth: AuthSettings = AuthSettings()
    model_config = SettingsConfigDict(env_file=".env")
    
settings = Settings()
