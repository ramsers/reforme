import secrets
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=1)

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(48)
