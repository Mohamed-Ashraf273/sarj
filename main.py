import logging

from fastapi import FastAPI

from backend.api.whatsapp import router as whatsapp_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(whatsapp_router)
