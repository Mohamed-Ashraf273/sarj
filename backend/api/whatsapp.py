import logging

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from backend.core.session_manager import session_manager
from backend.core.session import Session
from config import config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook")


@router.get("", response_class=PlainTextResponse)
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == config.WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified successfully.")
        return challenge

    raise HTTPException(status_code=403, detail="Verification failed.")


@router.post("")
async def receive_message(request: Request):
    body = await request.json()
    logger.info("Webhook POST received: %s", body)

    try:
        entry = body["entry"][0]
        change = entry["changes"][0]["value"]
        message = change["messages"][0]
    except (KeyError, IndexError):
        return {"status": "ok"}

    sender_phone = message["from"]
    text = message.get("text", {}).get("body", "")

    if not text:
        return {"status": "ok"}

    if sender_phone not in session_manager.sessions:
        session_manager.sessions[sender_phone] = Session(sender_phone)

    try:
        session = session_manager.open_session(sender_phone)
        interaction = session.generate_reply(text)
        session_manager.update_session_title(sender_phone, text)
        session_manager.save_message(sender_phone, interaction)

        if interaction.transfer:
            session_manager.close_session(sender_phone)
    except Exception:
        logger.exception("Failed to process message from %s", sender_phone)
        return {"status": "error"}

    _send_whatsapp_message(sender_phone, interaction.agent_reply)
    return {"status": "ok"}


def _send_whatsapp_message(to: str, text: str):
    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    r = requests.post(config.WHATSAPP_API_URL, headers=headers, json=payload)
    if not r.ok:
        logger.error("Failed to send WhatsApp message: %s %s", r.status_code, r.text)
