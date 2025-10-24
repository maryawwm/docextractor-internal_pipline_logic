from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    celery_broker: str
    celery_backend:str
    database_url: str

    minio_security: bool

    api_key: str
    document_path: str

    # OpenAI / Whisper settings
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_asr_model: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

app_settings = AppSettings()