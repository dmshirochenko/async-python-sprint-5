from minio import Minio

from src.core.config import settings

# Initialize MinIO client
minio_client = Minio(
    settings.minio_host,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False,
)
