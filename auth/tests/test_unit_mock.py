import uuid
import secrets
import pytest
from fastapi.testclient import TestClient

from dotenv import load_dotenv

load_dotenv()

from src.main import app
from src.models.schemas import UserRegistrationSchema, UserLoginSchema


client = TestClient(app)


@pytest.fixture
def generate_random_credentials():
    username = f"user_{uuid.uuid4()}"
    password = secrets.token_urlsafe(16)
    return username, password


def test_ping_database():
    response = client.get("/auth/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up and running"}


@pytest.fixture
async def test_user(generate_random_credentials):
    username, password = generate_random_credentials
    user_registration_info = UserRegistrationSchema(username=username, password=password)
    response = client.post("/auth/v1/user/registration", json=user_registration_info.dict())
    assert response.status_code == 201
    assert "username" in response.json()
    assert response.json()["username"] == username


@pytest.fixture
async def test_user(generate_random_credentials):
    credentials = UserLoginSchema(username=username, password=password)
    response = client.post("/auth/v1/user/login", json=credentials.dict())
    assert response.status_code == 200
    assert "username" in response.json()
    assert response.json()["username"] == username


@pytest.fixture
async def test_user(generate_random_credentials):
    credentials = UserLoginSchema(username=username, password=password)
    response_user = client.post("/auth/v1/user/login", json=credentials.dict())
    token = response_user.json().get("token")
    response = client.get("/auth/v1/user/by-token", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    assert "username" in response.json()
