from pydantic_settings import BaseSettings, SettingsConfigDict

from src.database.config import DBSettings
from src.auth.config import AuthSettings
from src.cors.config import CORSSettings

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth: AuthSettings = AuthSettings()
    cors: CORSSettings = CORSSettings()
    model_config = SettingsConfigDict(env_file=".env")
    
settings = Settings()
