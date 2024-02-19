from io import BytesIO
from datetime import datetime
from starlette.concurrency import run_in_threadpool

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from minio.error import S3Error

from src.models.models import File
from src.db.storage_connector import minio_client


async def ensure_bucket_exists(bucket_name: str) -> None:
    try:
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found")
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")


async def upload_file_to_minio(bucket_name: str, file_location: str, content: bytes) -> None:
    try:
        content_file = BytesIO(content)
        await run_in_threadpool(
            minio_client.put_object,
            bucket_name=bucket_name,
            object_name=file_location,
            data=content_file,
            length=len(content),
        )
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to MinIO: {str(e)}")


async def save_file_info(db: AsyncSession, user_id: str, file_name: str, file_location: str, file_size: int) -> File:
    try:
        file_info = File(
            user_id=user_id,
            file_name=file_name,
            created_at=datetime.now(),
            path=file_location,
            size=file_size,
            is_downloadable=True,
        )
        db.add(file_info)
        await db.commit()
        await db.refresh(file_info)
        return file_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save file info: {str(e)}")
