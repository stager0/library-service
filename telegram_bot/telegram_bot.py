import requests

def send_message(chat_id, text):
    url = "https://api.telegram.org/bot8096670982:AAFHrsLHupvzh1EhKJrs0Yce70G8Yn74URI/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, data=payload)
    return response.json()
