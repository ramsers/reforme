from apps.shared.models import TimestampModel, UUIDModel
from django.db import models
from apps.user.models import User


class Class(TimestampModel, UUIDModel):
    name = models.CharField(max_length=255)
    size = models.IntegerField(default=15)
    date = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes')

    class Meta:
        db_table = "classes"
