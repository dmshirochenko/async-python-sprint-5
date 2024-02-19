import uuid
from starlette.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse

from fastapi import File as FastAPIFile
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from minio.error import S3Error

from src.core.config import settings
from src.db.db_connector import get_async_session
from src.db.storage_connector import minio_client
from src.models.models import File
from src.models.schemas import FileInfoResponse, FileListResponse
from src.services.utils import ensure_bucket_exists, upload_file_to_minio, save_file_info

router = APIRouter()


async def get_current_user():
    return {"user_id": 1}


@router.get("/file-storage/v1/ping")
async def ping_service():
    return {"message": "Service is up and running"}


@router.get("/file-storage/files/list", response_model=FileListResponse)
async def list_files(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    async with db as session:
        result = await session.execute(select(File).where(File.user_id == user["user_id"]))
        files = result.scalars().all()
        files_info = [FileInfoResponse.from_orm(file) for file in files]
        return FileListResponse(user_id=user["user_id"], files=files_info)


@router.post("/file-storage/files/upload", response_model=FileInfoResponse)
async def upload_file(
    upload_file: UploadFile = FastAPIFile(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    bucket_name = settings.minio_bucket
    file_name = f"{uuid.uuid4()}-{upload_file.filename}"
    file_location = f"{user['user_id']}/{file_name}"

    await ensure_bucket_exists(bucket_name)
    content = await upload_file.read()
    await upload_file_to_minio(bucket_name, file_location, content)
    file_info = await save_file_info(db, user["user_id"], file_name, file_location, len(content))

    return FileInfoResponse.from_orm(file_info)


@router.get("/file-storage/files/download")
async def download_file(
    file_id: uuid.UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)
):
    async with db as session:
        result = await session.execute(select(File).where(File.id == file_id, File.user_id == user["user_id"]))
        file = result.scalars().first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        try:
            response = await run_in_threadpool(minio_client.get_object, settings.minio_bucket, file.path)
            return StreamingResponse(
                response.stream(32 * 1024),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename={file.file_name}"},
            )
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve file from storage: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
