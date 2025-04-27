from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import paramiko
from ..database.database import get_db
from ..database.models import Tower, Server
from ..websocket.connection_manager import manager

router = APIRouter(prefix="/towers", tags=["towers"])

class TowerCreate(BaseModel):
    name: str
    ip_address: str
    device_type: str  # Mimosa or UBNT
    username: str
    password: str
    default_speed: float = None
    min_signal: float
    max_signal: float
    alternate_frequency: str = None
    notes: str = None
    server_id: int

class TowerResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    device_type: str
    default_speed: float = None
    min_signal: float
    max_signal: float
    alternate_frequency: str = None
    notes: str = None
    server_id: int
    created_at: datetime

    class Config:
        orm_mode = True

def check_tower_connection(ip: str, username: str, password: str, device_type: str):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)
        ssh.close()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")

@router.post("/", response_model=TowerResponse)
async def create_tower(tower: TowerCreate, db: Session = Depends(get_db)):
    # Verify server exists
    server = db.query(Server).filter(Server.id == tower.server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Test connection to tower
    check_tower_connection(tower.ip_address, tower.username, tower.password, tower.device_type)

    try:
        db_tower = Tower(**tower.dict())
        db.add(db_tower)
        db.commit()
        db.refresh(db_tower)

        # Notify connected clients
        await manager.broadcast({
            "type": "tower_added",
            "data": TowerResponse.from_orm(db_tower).dict()
        })

        return db_tower
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[TowerResponse])
def get_towers(db: Session = Depends(get_db)):
    return db.query(Tower).all()

@router.get("/{tower_id}", response_model=TowerResponse)
def get_tower(tower_id: int, db: Session = Depends(get_db)):
    tower = db.query(Tower).filter(Tower.id == tower_id).first()
    if tower is None:
        raise HTTPException(status_code=404, detail="Tower not found")
    return tower

@router.delete("/{tower_id}")
async def delete_tower(tower_id: int, db: Session = Depends(get_db)):
    tower = db.query(Tower).filter(Tower.id == tower_id).first()
    if tower is None:
        raise HTTPException(status_code=404, detail="Tower not found")
    
    db.delete(tower)
    db.commit()

    await manager.broadcast({
        "type": "tower_deleted",
        "data": {"id": tower_id}
    })

    return {"message": "Tower deleted successfully"}

@router.get("/{tower_id}/signal")
async def get_tower_signal(tower_id: int, db: Session = Depends(get_db)):
    tower = db.query(Tower).filter(Tower.id == tower_id).first()
    if tower is None:
        raise HTTPException(status_code=404, detail="Tower not found")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(tower.ip_address, username=tower.username, password=tower.password)

        if tower.device_type.upper() == "UBNT":
            stdin, stdout, stderr = ssh.exec_command("mca-status | grep signal")
            signal_data = stdout.read().decode()
        elif tower.device_type.upper() == "MIMOSA":
            stdin, stdout, stderr = ssh.exec_command("cli-json-request GET link/act/radioStatus")
            signal_data = stdout.read().decode()
        
        ssh.close()
        return {"signal": signal_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get signal strength: {str(e)}")