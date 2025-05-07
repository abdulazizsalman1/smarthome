from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import json
import os
from backend import models, auth
from backend.database import engine, get_db
from pydantic import BaseModel
from datetime import timedelta, datetime

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route to serve the login page
@app.get("/")
async def read_root():
    return FileResponse("frontend/login.html")

# Serve other frontend pages
@app.get("/login")
async def read_login():
    return FileResponse("frontend/login.html")

@app.get("/register")
async def read_register():
    return FileResponse("frontend/register.html")

@app.get("/home")
async def read_home():
    return FileResponse("frontend/home.html")

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        pass
        from_attributes = True

class HomeCreate(BaseModel):
    name: str
    address: str

class HomeResponse(BaseModel):
    id: int
    name: str
    address: str
    owner_id: int
    created_at: datetime

    class Config:
        pass
        from_attributes = True

class RoomCreate(BaseModel):
    name: str
    home_id: int

class RoomResponse(BaseModel):
    id: int
    name: str
    home_id: int
    created_at: datetime

    class Config:
        pass
        from_attributes = True

class DeviceCreate(BaseModel):
    name: str
    type: str
    room_id: int

class DeviceResponse(BaseModel):
    id: int
    name: str
    type: str
    status: bool
    brightness: float
    color: str
    position: float
    room_id: int
    created_at: datetime
    last_updated: datetime

    class Config:
        pass
        from_attributes = True

class DeviceUpdate(BaseModel):
    status: bool = None
    brightness: float = None
    color: str = None
    position: float = None

# User endpoints
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Home endpoints
@app.post("/homes/", response_model=HomeResponse)
def create_home(home: HomeCreate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    db_home = models.Home(**home.dict(), owner_id=current_user.id)
    db.add(db_home)
    db.commit()
    db.refresh(db_home)
    return db_home

@app.get("/homes/", response_model=List[HomeResponse])
def read_homes(current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    return db.query(models.Home).filter(models.Home.owner_id == current_user.id).all()

# Room endpoints
@app.post("/rooms/", response_model=RoomResponse)
def create_room(room: RoomCreate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    home = db.query(models.Home).filter(models.Home.id == room.home_id).first()
    if not home or home.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Home not found")
    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@app.get("/rooms/{home_id}", response_model=List[RoomResponse])
def read_rooms(home_id: int, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    home = db.query(models.Home).filter(models.Home.id == home_id).first()
    if not home or home.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Home not found")
    return db.query(models.Room).filter(models.Room.home_id == home_id).all()

# Device endpoints
@app.post("/devices/", response_model=DeviceResponse)
def create_device(device: DeviceCreate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == device.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    home = db.query(models.Home).filter(models.Home.id == room.home_id).first()
    if not home or home.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Home not found")
    db_device = models.Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.get("/devices/{room_id}", response_model=List[DeviceResponse])
def read_devices(room_id: int, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    home = db.query(models.Home).filter(models.Home.id == room.home_id).first()
    if not home or home.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Home not found")
    return db.query(models.Device).filter(models.Device.room_id == room_id).all()

@app.patch("/devices/{device_id}", response_model=DeviceResponse)
def update_device(device_id: int, device_update: DeviceUpdate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    room = db.query(models.Room).filter(models.Room.id == device.room_id).first()
    home = db.query(models.Home).filter(models.Home.id == room.home_id).first()
    if not home or home.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Home not found")
    
    update_data = device_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)
    
    db.commit()
    db.refresh(device)
    return device 