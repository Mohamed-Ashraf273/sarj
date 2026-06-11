from fastapi import APIRouter, Response

from backend.core.session_manager import session_manager

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