from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ip_address = Column(String, unique=True)
    username = Column(String)
    password = Column(String)
    server_type = Column(String)  # main/secondary
    default_speed = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="server")
    towers = relationship("Tower", back_populates="server")

class Tower(Base):
    __tablename__ = "towers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ip_address = Column(String, unique=True)
    device_type = Column(String)  # Mimosa/UBNT
    username = Column(String)
    password = Column(String)
    default_speed = Column(Float, nullable=True)
    min_signal = Column(Float)
    max_signal = Column(Float)
    alternate_frequency = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    server_id = Column(Integer, ForeignKey("servers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server", back_populates="towers")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    speed_limit = Column(Float)
    expiry_date = Column(DateTime)
    notes = Column(String, nullable=True)
    server_id = Column(Integer, ForeignKey("servers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server", back_populates="users")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="admin")  # يمكن إضافة أدوار مختلفة مستقبلاً