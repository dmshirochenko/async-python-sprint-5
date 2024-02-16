from fastapi import APIRouter

router = APIRouter()


@router.get("/v1/ping")
async def ping_database():
    return {"message": "Service is up and running"}
