import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from src.db.db_connector import get_async_session
from src.models.models import User
from src.models.schemas import UserSchema, UserLoginSchema, UserRegistrationSchema
import src.services.user_auth_services as user_auth_services

router = APIRouter()


@router.get("/auth/v1/ping")
async def ping_database():
    return {"message": "Service is up and running"}


@router.post("/auth/v1/user/registration", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def register_user(
    user_registration_info: UserRegistrationSchema, db: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Register a new user with a given username.
    """
    token = secrets.token_urlsafe(32)
    user_password_hash = user_auth_services.hash_password(user_registration_info.password)
    new_user = User(username=user_registration_info.username, token=token, hashed_password=user_password_hash)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken")


@router.post("/auth/v1/user/login", response_model=UserSchema)
async def login_user(credentials: UserLoginSchema, db: AsyncSession = Depends(get_async_session)) -> Any:
    async with db as session:
        query = select(User).filter(User.username == credentials.username)
        result = await session.execute(query)
        user = result.scalars().first()
        if user and user_auth_services.verify_password(credentials.password, user.hashed_password):
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


@router.get("/auth/v1/user/by-token", response_model=UserSchema)
async def get_current_user(db: AsyncSession = Depends(get_async_session), authorization: str = Header(...)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format.")

    token = authorization[7:]

    async with db as session:
        query = select(User).filter(User.token == token)
        result = await session.execute(query)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found with provided token")

    return user
