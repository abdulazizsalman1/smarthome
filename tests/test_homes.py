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
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def setup_client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_token():
    # Register and login to get token
    test_client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    response = test_client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    return response.json()["access_token"]

def test_create_home(auth_token):
    response = test_client.post("/homes/", 
        json={
            "name": "Test Home",
            "address": "123 Test St"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Home"
    assert data["address"] == "123 Test St"
    assert "id" in data

def test_get_homes(auth_token):
    # Create a home first
    test_client.post("/homes/", 
        json={
            "name": "Test Home",
            "address": "123 Test St"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get homes
    response = test_client.get("/homes/", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Home"

def test_create_home_unauthorized():
    response = test_client.post("/homes/", 
        json={
            "name": "Test Home",
            "address": "123 Test St"
        }
    )
    assert response.status_code == 401

def test_get_homes_unauthorized():
    response = test_client.get("/homes/")
    assert response.status_code == 401 