import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db
from backend import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, backend="asgi")

@pytest.fixture(autouse=True)
def setup_database():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def setup_client():
    with TestClient(app) as test_client:
        yield test_client

def test_register_user():
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_username():
    # First registration
    client.post("/users/", json={
        "username": "testuser",
        "email": "test1@example.com",
        "password": "testpass123"
    })
    
    # Second registration with same username
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test2@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_login_success():
    # Register user first
    client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Login
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    # Register user first
    client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Login with wrong password
    response = client.post("/token", data={
        "username": "testuser",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"] 