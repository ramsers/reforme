from django.contrib.auth.base_user import AbstractBaseUser
from apps.shared.models import TimestampModel, UUIDModel
from django.db import models
from apps.user.value_objects import Role


class User(AbstractBaseUser, UUIDModel, TimestampModel):
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    USERNAME_FIELD = 'email'
    password = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        db_table = "users"




class Account(UUIDModel, TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="account")
    bio = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=255, default="EST")

    class Meta:
        db_table = "accounts"