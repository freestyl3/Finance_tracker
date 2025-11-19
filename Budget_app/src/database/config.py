from pydantic_settings import BaseSettings, SettingsConfigDict

class DBSettings(BaseSettings):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        extra="ignore"
    )

    @property
    def url(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@" \
               f"{self.HOST}:{self.PORT}/{self.NAME}"