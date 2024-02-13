from fastapi import FastAPI
from src.api.v1 import users_routes


app = FastAPI()

app.include_router(users_routes.router)
