import aiofiles
import uuid
from datetime import datetime

from fastapi import File as FastAPIFile
from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.db_connector import get_async_session
from src.models.models import File
from src.models.schemas import FileInfoResponse, FileListResponse

router = APIRouter()


async def get_current_user():
    return {"user_id": 1}


@router.get("/v1/ping")
async def ping_database():
    return {"message": "Service is up and running"}


@router.get("/files/list", response_model=FileListResponse)
async def list_files(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    async with db as session:
        result = await session.execute(select(File).where(File.user_id == user["user_id"]))
        files = result.scalars().all()
        files_info = [FileInfoResponse.from_orm(file) for file in files]
        return FileListResponse(user_id=user["user_id"], files=files_info)


@router.post("/files/upload", response_model=FileInfoResponse)
async def upload_file(
    upload_file: UploadFile = FastAPIFile(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    file_location = f"{settings.base_dir_local}/storage/{upload_file.filename}"

    existing_file = await db.execute(select(File).where(File.path == file_location))
    existing_file = existing_file.scalars().first()
    if existing_file:
        raise HTTPException(status_code=400, detail="File already exists with the given path")

    async with aiofiles.open(file_location, "wb") as out_file:
        content = await upload_file.read()
        await out_file.write(content)

    file_info = File(
        user_id=user["user_id"],
        file_name=upload_file.filename,
        created_at=datetime.now(),
        path=file_location,
        size=len(content),
        is_downloadable=True,
    )
    db.add(file_info)
    await db.commit()
    await db.refresh(file_info)

    return FileInfoResponse.from_orm(file_info)


@router.get("/files/download")
async def download_file(
    file_id: uuid.UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)
):
    async with db as session:
        result = await session.execute(select(File).where(File.id == file_id, File.user_id == user["user_id"]))
        file = result.scalars().first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Make sure the file path is correct and accessible
        file_path = file.path  # Ensure this is the absolute path to the file
        return FileResponse(path=file_path, filename=file.file_name, media_type="application/octet-stream")
