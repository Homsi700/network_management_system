from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ..database.database import get_db
from ..database.models import User, Server
from .mikrotik import MikrotikAPI
from ..websocket.connection_manager import manager

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    password: str
    speed_limit: float
    expiry_date: datetime
    notes: str = None
    server_id: int

class UserResponse(BaseModel):
    id: int
    username: str
    speed_limit: float
    expiry_date: datetime
    notes: str = None
    server_id: int
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verify server exists
    server = db.query(Server).filter(Server.id == user.server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        # Create user on Mikrotik router
        mikrotik = MikrotikAPI(server.ip_address, server.username, server.password)
        mikrotik.add_pppoe_user(user.username, user.password, user.speed_limit)

        # Create user in database
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Notify connected clients
        await manager.broadcast({
            "type": "user_added",
            "data": UserResponse.from_orm(db_user).dict()
        })

        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    server = db.query(Server).filter(Server.id == user.server_id).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        # Remove user from Mikrotik router
        mikrotik = MikrotikAPI(server.ip_address, server.username, server.password)
        mikrotik.remove_pppoe_user(user.username)

        # Remove user from database
        db.delete(user)
        db.commit()

        # Notify connected clients
        await manager.broadcast({
            "type": "user_deleted",
            "data": {"id": user_id}
        })

        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/speed")
async def update_user_speed(
    user_id: int, 
    speed_limit: float,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    server = db.query(Server).filter(Server.id == user.server_id).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        # Update speed on Mikrotik router
        mikrotik = MikrotikAPI(server.ip_address, server.username, server.password)
        mikrotik.update_user_speed(user.username, speed_limit)

        # Update speed in database
        user.speed_limit = speed_limit
        db.commit()

        # Notify connected clients
        await manager.broadcast({
            "type": "user_speed_updated",
            "data": {"id": user_id, "speed_limit": speed_limit}
        })

        return {"message": "User speed updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))