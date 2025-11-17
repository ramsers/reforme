from apps.shared.models import TimestampModel, UUIDModel
from django.db import models
from apps.user.models import User
from apps.classes.models import Classes


class Booking(TimestampModel, UUIDModel):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_class')
    booked_class = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)

    class Meta:
        db_table = "booking"
