from fastapi import FastAPI
from src.api.v1 import file_storage_routes


app = FastAPI()

app.include_router(file_storage_routes.router)
