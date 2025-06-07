from django.urls import path

from .views import TelegramWebhookView


app_name = "telegram_bot"
urlpatterns = [
    path("webhook/", TelegramWebhookView.as_view(), name="telegram_webhook"),
]
