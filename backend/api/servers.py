from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ..database.database import get_db
from ..database.models import Server
from .mikrotik import MikrotikAPI
from ..websocket.connection_manager import manager

router = APIRouter(prefix="/servers", tags=["servers"])

class ServerCreate(BaseModel):
    name: str
    ip_address: str
    username: str
    password: str
    server_type: str
    default_speed: float = None

class ServerResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    server_type: str
    default_speed: float = None
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=ServerResponse)
async def create_server(server: ServerCreate, db: Session = Depends(get_db)):
    try:
        # Test connection to Mikrotik device
        mikrotik = MikrotikAPI(server.ip_address, server.username, server.password)
        mikrotik.connect()
        
        db_server = Server(**server.dict())
        db.add(db_server)
        db.commit()
        db.refresh(db_server)
        
        # Notify connected clients
        await manager.broadcast({
            "type": "server_added",
            "data": ServerResponse.from_orm(db_server).dict()
        })
        
        return db_server
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ServerResponse])
def get_servers(db: Session = Depends(get_db)):
    return db.query(Server).all()

@router.get("/{server_id}", response_model=ServerResponse)
def get_server(server_id: int, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.delete("/{server_id}")
async def delete_server(server_id: int, db: Session = Depends(get_db)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    
    db.delete(server)
    db.commit()
    
    await manager.broadcast({
        "type": "server_deleted",
        "data": {"id": server_id}
    })
    
    return {"message": "Server deleted successfully"}