from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    reconnect_window_s: int = 30
    audio_buffer_seconds: int = 30


def get_settings() -> Settings:
    return Settings()
