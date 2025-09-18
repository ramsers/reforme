from django.db import models


class Role(models.TextChoices):
    INSTRUCTOR = 'INSTRUCTOR'
    CLIENT = 'CLIENT'
    ADMIN = 'ADMIN'
