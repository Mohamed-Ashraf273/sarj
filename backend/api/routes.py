from fastapi import APIRouter, Response, Header, HTTPException

from backend.core.session_manager import session_manager
from config import config

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Sarj API is running!"}


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.head("/health")
async def health_head():
    return Response(status_code=200)


@router.post("/sessions")
async def create_session():
    session_id = session_manager.create_session()
    return {"session_id": session_id}


@router.get("/sessions")
async def list_sessions():
    return {"sessions": session_manager.list_sessions()}


@router.post("/sessions/cleanup")
async def cleanup_sessions(x_cron_secret: str = Header(None)):
    if x_cron_secret != config.CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    count = len(session_manager.sessions)
    session_manager.sessions.clear()
    return {"status": "ok", "cleared": count}