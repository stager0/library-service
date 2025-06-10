from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
import json
import requests
from environ import environ

from telegram_bot.models import UserProfile


env = environ.Env()
environ.Env.read_env()


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{env('BOT_TOKEN')}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, data=payload)


class TelegramWebhookView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('UTF-8'))

        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        if text == "/start":
            send_message(chat_id, "Please, enter your email to connect to your account.")
        elif "@" in text:
            self.check_email_and_respond(chat_id, text)
        else:
            send_message(chat_id, "Invalid input. Please enter a valid email.")

        return JsonResponse({"status": "ok"})

    def check_email_and_respond(self, chat_id, email):
        user_profile_emails = UserProfile.objects.values_list("email", flat=True)
        user_profile_ids = UserProfile.objects.values_list("telegram_chat_id", flat=True)
        if email not in user_profile_emails and chat_id not in user_profile_ids:
            UserProfile.objects.create(telegram_chat_id=chat_id, email=email)
            send_message(chat_id, "You were successfully logged in!")

        elif email in user_profile_emails or chat_id in user_profile_ids:
            UserProfile.objects.get(telegram_chat_id=chat_id)
            send_message(chat_id, "You were successfully logged in!")
        else:
            send_message(chat_id, "No account found with this email. Please register on the website.")