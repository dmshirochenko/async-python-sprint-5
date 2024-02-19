import uuid
import secrets
import pytest
from fastapi.testclient import TestClient

from dotenv import load_dotenv

load_dotenv()

from src.main import app

client = TestClient(app)

def test_ping_service():
    response = client.get("/file-storage/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up and running"}
