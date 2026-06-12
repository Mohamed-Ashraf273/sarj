import logging
import re

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from backend.api.routes import router as sessions_router
from backend.core.session_manager import session_manager
from backend.core.session import Session
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(sessions_router)


@app.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == config.WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified successfully.")
        return challenge

    raise HTTPException(status_code=403, detail="Verification failed.")


@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    logger.info("Webhook POST received: %s", body)

    platform = body.get("object", "")

    if platform == "whatsapp_business_account" or platform == "":
        return await _handle_whatsapp(body)
    elif platform == "instagram":
        return await _handle_instagram(body)
    else:
        logger.warning("Unknown platform: %s", platform)
        return {"status": "ok"}


async def _handle_whatsapp(body: dict):
    try:
        entry = body["entry"][0]
        change = entry["changes"][0]["value"]
        message = change["messages"][0]
    except (KeyError, IndexError):
        return {"status": "ok"}

    sender_id = message["from"]
    text = message.get("text", {}).get("body", "")

    if not text:
        return {"status": "ok"}

    interaction = _process_message(sender_id, text)
    if interaction is None:
        return {"status": "error"}

    _send_whatsapp_message(sender_id, md_to_whatsapp(interaction.agent_reply))
    return {"status": "ok", "reply": interaction.agent_reply}


async def _handle_instagram(body: dict):
    try:
        entry = body["entry"][0]
        messaging = entry["messaging"][0]
        sender_id = messaging["sender"]["id"]
        text = messaging.get("message", {}).get("text", "")
    except (KeyError, IndexError):
        return {"status": "ok"}

    if not text:
        return {"status": "ok"}

    interaction = _process_message(sender_id, text)
    if interaction is None:
        return {"status": "error"}

    _send_instagram_message(sender_id, interaction.agent_reply)
    return {"status": "ok", "reply": interaction.agent_reply}


def _process_message(sender_id: str, text: str):
    if sender_id not in session_manager.sessions:
        session_manager.sessions[sender_id] = Session(sender_id)

    try:
        session = session_manager.open_session(sender_id)
        interaction = session.generate_reply(text)
        session_manager.update_session_title(sender_id, text)
        session_manager.save_message(sender_id, interaction)

        if interaction.end_chat:
            session_manager.close_session(sender_id)

        return interaction
    except Exception:
        logger.exception("Failed to process message from %s", sender_id)
        return None


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


def _send_instagram_message(recipient_id: str, text: str):
    url = "https://graph.facebook.com/v25.0/me/messages"
    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    r = requests.post(url, headers=headers, json=payload)
    if not r.ok:
        logger.error("Failed to send Instagram message: %s %s", r.status_code, r.text)


def md_to_whatsapp(text: str) -> str:
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"_\1_", text)
    text = re.sub(r"^\s*[-*]\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"^[-_*]{3,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()