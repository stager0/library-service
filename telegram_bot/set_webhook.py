import requests
from environ import environ

env = environ.Env()
environ.Env.read_env()

response = requests.post(f"https://api.telegram.org/bot{env('BOT_TOKEN')}/setWebhook", data={"url": {env("WEBHOOK_URL")}})
print(response.json())
