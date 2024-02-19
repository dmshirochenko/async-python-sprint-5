import os

from pydantic import BaseSettings, Field


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env_file = ".env"
ENV_FILE_PATH = os.path.join(BASE_DIR, env_file)


class Settings(BaseSettings):
    app_debug_level: str = Field("INFO", env="APP_DEBUG_LEVEL")
    base_dir: str = Field(BASE_DIR)
    env_name: str = os.getenv("ENV_NAME")
    db_url: str = os.getenv("FILE_STORAGE_POSTGRES_DATABASE_URL")
    auth_service_url: str = os.getenv("AUTH_SERVER_URL")
    minio_host: str = os.getenv("MINIO_HOSTNAME")
    minio_url: str = os.getenv("MINIO_URL")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY")
    minio_secure: bool = os.getenv("MINIO_SECURE")
    minio_bucket: str = os.getenv("MINIO_BUCKET")

    class Config:
        env_file = ENV_FILE_PATH


settings = Settings()
