from sqlalchemy import Boolean, Column, Integer, String

from src.db.db_connector import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth_service"}

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    token = Column(String)
    is_active = Column(Boolean, default=True)
