import requests
import dotenv
import os

dotenv.load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
TO = "201004538215"  # recipient number, country code, no +


url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

payload = {
    "messaging_product": "whatsapp",
    "to": TO,
    "type": "text",
    "text": {"body": "Hello Mohamed, this is a normal text message from me."},
}

r = requests.post(url, headers=headers, json=payload)
print(r.status_code)
print(r.json())