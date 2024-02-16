from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from src.core.config import settings

engine = create_async_engine(settings.db_url, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session
