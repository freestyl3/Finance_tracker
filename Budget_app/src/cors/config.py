from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class CORSSettings(BaseSettings):
    ALLOW_ORIGINS: list[str] | str
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True

    @field_validator("ALLOW_ORIGINS", "ALLOW_METHODS", "ALLOW_HEADERS", mode="before")
    @classmethod
    def split_if_string(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CORS_",
        extra="ignore"
    )