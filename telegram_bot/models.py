from django.db import models

class UserProfile(models.Model):
    telegram_chat_id = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
