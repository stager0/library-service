import os

import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.post(f"https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/setWebhook", data={"url": {os.getenv("WEBHOOK_URL")}})
print(response.json())
