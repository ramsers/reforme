from rest_framework import serializers

from apps.booking.serializers import BookingClientSerializer
from apps.classes.models import Classes
from apps.user.serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist


class ClassesSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()
    bookings_count = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    bookings = serializers.SerializerMethodField()

    def get_instructor(self, obj):
        try:
            return UserSerializer(obj.instructor).data if obj.instructor else None
        except ObjectDoesNotExist:
            return None

    def get_bookings_count(self, obj):
        return obj.bookings.count()

    def get_is_full(self, obj):
        return obj.bookings.count() >= int(obj.size)

    def get_bookings(self, obj):
        try:
            return BookingClientSerializer(obj.bookings.all(), many=True, default=[]).data
        except ObjectDoesNotExist:
            return None

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
        ]
