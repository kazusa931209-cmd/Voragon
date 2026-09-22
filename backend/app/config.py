from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    reconnect_window_s: int = 30
    heartbeat_idle_timeout_s: int = 45
    audio_buffer_seconds: int = 30
    audio_reorder_buffer_ms: int = 100
    vad_backend: str = "silero"
    vad_speech_threshold: float = 0.5
    vad_min_speech_duration_ms: int = 250
    vad_min_silence_duration_ms: int = 500
    vad_speech_pad_ms: int = 300
    asr_backend: str = "faster_whisper"
    asr_model: str = "large-v3-turbo"
    asr_partial_interval_ms: int = 300


def get_settings() -> Settings:
    return Settings()
