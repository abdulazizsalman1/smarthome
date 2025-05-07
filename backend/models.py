from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    homes = relationship("Home", back_populates="owner")
    created_at = Column(DateTime, default=datetime.utcnow)

class Home(Base):
    __tablename__ = "homes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="homes")
    rooms = relationship("Room", back_populates="home")
    created_at = Column(DateTime, default=datetime.utcnow)

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    home_id = Column(Integer, ForeignKey("homes.id"))
    home = relationship("Home", back_populates="rooms")
    devices = relationship("Device", back_populates="room")
    created_at = Column(DateTime, default=datetime.utcnow)

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # light, lock, alarm, blind
    status = Column(Boolean, default=False)
    brightness = Column(Float, default=100.0)  # for lights
    color = Column(String, default="#FFFFFF")  # for lights
    position = Column(Float, default=0.0)  # for blinds (0-100)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    room = relationship("Room", back_populates="devices")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
