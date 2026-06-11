import dotenv

dotenv.load_dotenv()

class Config:
    ACCESS_TOKEN = dotenv.get_key(".env", "ACCESS_TOKEN")
    PHONE_NUMBER_ID = dotenv.get_key(".env", "PHONE_NUMBER_ID")
    WEBHOOK_VERIFY_TOKEN = dotenv.get_key(".env", "WEBHOOK_VERIFY_TOKEN")
    WHATSAPP_API_URL = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"


config = Config()