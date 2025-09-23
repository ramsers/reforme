from apps.shared.models import TimestampModel, UUIDModel
from django.db import models
from apps.user.models import User


class Classes(TimestampModel, UUIDModel):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=255)
    size = models.IntegerField(default=15)
    length = models.IntegerField(default=45)
    date = models.DateTimeField(null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes', blank=True, null=True)

    class Meta:
        db_table = "classes"
        ordering = ['-created_at']

