import uuid

import httpx
from fastapi import File as FastAPIFile
from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.db_connector import get_async_session
from src.models.models import File
from src.models.schemas import FileInfoResponse, FileListResponse
from src.services.utils import ensure_bucket_exists, upload_file_to_minio, save_file_info

router = APIRouter()


async def get_token_header(request: Request):
    if "Authorization" not in request.headers:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    return request.headers["Authorization"].split(" ")[1]


async def get_current_user(token: str = Depends(get_token_header)):
    auth_url = f"{settings.auth_service_url}/auth/v1/user/by-token"
    async with httpx.AsyncClient() as client:
        response = await client.get(auth_url, headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Invalid token or auth server error")
        user_data = response.json()
        if not user_data["is_active"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return {"user_id": user_data["id"], "username": user_data["username"]}


@router.get("/file-storage/v1/ping")
async def ping_service():
    return {"message": "Service is up and running"}


@router.get("/file-storage/v1/files/list", response_model=FileListResponse)
async def list_files(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)):
    async with db as session:
        result = await session.execute(select(File).where(File.user_id == user["user_id"]))
        files = result.scalars().all()
        files_info = [FileInfoResponse.from_orm(file) for file in files]
        return FileListResponse(user_id=user["user_id"], files=files_info)


@router.post("/file-storage/v1/files/upload", response_model=FileInfoResponse)
async def upload_file(
    upload_file: UploadFile = FastAPIFile(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    bucket_name = settings.minio_bucket
    file_name = f"{uuid.uuid4()}-{upload_file.filename}"
    file_location = f"static/{user['user_id']}/{file_name}"

    await ensure_bucket_exists(bucket_name)
    content = await upload_file.read()
    await upload_file_to_minio(bucket_name, file_location, content)
    file_info = await save_file_info(db, user["user_id"], file_name, file_location, len(content))

    return FileInfoResponse.from_orm(file_info)


@router.get("/file-storage/v1/files/download")
async def download_file(
    file_id: uuid.UUID, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_async_session)
):
    async with db as session:
        result = await session.execute(select(File).where(File.id == file_id, File.user_id == user["user_id"]))
        file = result.scalars().first()
        if not file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        file_url = f"{settings.minio_url}/{settings.minio_bucket}/{file.path}"
        return RedirectResponse(url=file_url)
