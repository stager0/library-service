from django.db import models

class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    telegram_chat_id = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.email
