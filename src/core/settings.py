from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    celery_broker: str
    celery_backend:str
    database_url: str

    minio_security: bool

    api_key: str
    document_path: str

    model_config = SettingsConfigDict(env_file=".env")

app_settings = AppSettings()