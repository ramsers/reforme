from apps.shared.models import TimestampModel, UUIDModel
from django.db import models
from apps.user.models import User
from apps.classes.value_objects import ClassRecurrenceType


class Classes(TimestampModel, UUIDModel):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=255)
    size = models.IntegerField(default=15)
    length = models.IntegerField(default=45)
    date = models.DateTimeField(null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes', blank=True, null=True)
    recurrence_type = models.CharField(
        max_length=10,
        choices=ClassRecurrenceType.choices,
        blank=True,
        null=True
    )
    recurrence_days = models.JSONField(
        blank=True,
        null=True,
        help_text="List of weekdays for weekly recurrence, e.g., [0, 2] for Mon & Wed"
    )
    parent_class = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="child_classes",
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = "classes"
        ordering = ['date']
