from rest_framework import serializers

from apps.booking.serializers import BookingClientSerializer
from apps.classes.models import Classes
from apps.user.serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist


class ClassesSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    bookings_count = serializers.IntegerField(source="bookings.count", read_only=True)
    is_full = serializers.SerializerMethodField()
    bookings = BookingClientSerializer(source="bookings.all", many=True, read_only=True)

    def get_is_full(self, obj):
        return obj.bookings.count() >= int(obj.size)

    class Meta:
        model = Classes
        fields = [
            "id",
            "title",
            "description",
            "size",
            "length",
            "date",
            "instructor",
            "bookings_count",
            "is_full",
            "bookings",
            "recurrence_type",
            "recurrence_days",
        ]
