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

@pytest.fixture
def auth_token():
    # Register and login to get token
    client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    return response.json()["access_token"]

@pytest.fixture
def home_id(auth_token):
    response = client.post("/homes/", 
        json={
            "name": "Test Home",
            "address": "123 Test St"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    return response.json()["id"]

@pytest.fixture
def room_id(auth_token, home_id):
    response = client.post("/rooms/", 
        json={
            "name": "Test Room",
            "home_id": home_id
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    return response.json()["id"]

def test_create_device(auth_token, room_id):
    response = client.post("/devices/", 
        json={
            "name": "Test Light",
            "type": "light",
            "room_id": room_id
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Light"
    assert data["type"] == "light"
    assert data["room_id"] == room_id

def test_get_devices(auth_token, room_id):
    # Create a device first
    client.post("/devices/", 
        json={
            "name": "Test Light",
            "type": "light",
            "room_id": room_id
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get devices
    response = client.get(f"/devices/{room_id}", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Light"

def test_update_device(auth_token, room_id):
    # Create a device first
    response = client.post("/devices/", 
        json={
            "name": "Test Light",
            "type": "light",
            "room_id": room_id
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    device_id = response.json()["id"]
    
    # Update device
    response = client.patch(f"/devices/{device_id}", 
        json={
            "status": True,
            "brightness": 75,
            "color": "#FF0000"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == True
    assert data["brightness"] == 75
    assert data["color"] == "#FF0000"

def test_create_device_unauthorized(room_id):
    response = client.post("/devices/", 
        json={
            "name": "Test Light",
            "type": "light",
            "room_id": room_id
        }
    )
    assert response.status_code == 401

def test_get_devices_unauthorized(room_id):
    response = client.get(f"/devices/{room_id}")
    assert response.status_code == 401 