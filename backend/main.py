from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from .api import servers, users, towers, auth
from .database.database import engine, Base
from .websocket.connection_manager import manager
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Network Management System",
    description="نظام إدارة شبكة الإنترنت المحلية",
    version="1.0.0"
)

# CORS middleware with more specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for assets
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/dashboard")
async def get_dashboard():
    try:
        return FileResponse("frontend/dashboard.html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Page not found")


# Include routers
app.include_router(auth.router)
app.include_router(servers.router)
app.include_router(users.router)
app.include_router(towers.router)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_to_client({"message": "Received your message!"}, client_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        await manager.broadcast({"message": f"Client #{client_id} left the chat"})

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/donation")
async def donation():
    return FileResponse("frontend/donation.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)