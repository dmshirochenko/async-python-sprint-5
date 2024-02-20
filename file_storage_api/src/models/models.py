import uuid

from sqlalchemy import Column, Text, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.db.db_connector import Base


class File(Base):
    __tablename__ = "files"
    __table_args__ = {"schema": "file_storage_service"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, nullable=False)
    file_name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    path = Column(Text, nullable=False, unique=True)
    size = Column(Integer, nullable=False)
    is_downloadable = Column(Boolean, default=True, nullable=False)
