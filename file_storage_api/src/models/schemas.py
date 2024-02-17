from uuid import UUID
from typing import List
from datetime import datetime

from pydantic import BaseModel, Field


class FileInfoResponse(BaseModel):
    id: UUID
    user_id: int
    file_name: str
    created_at: datetime
    path: str
    size: int
    is_downloadable: bool

    class Config:
        orm_mode = True


class FileListResponse(BaseModel):
    user_id: int = Field(..., description="The ID of the user account")
    files: List[FileInfoResponse] = Field(..., description="List of files belonging to the user")
