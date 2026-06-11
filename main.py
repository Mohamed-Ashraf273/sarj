import logging

from fastapi import FastAPI

from backend.api.routes import router as sessions_router
from backend.api.whatsapp import router as whatsapp_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(sessions_router)
app.include_router(whatsapp_router)
