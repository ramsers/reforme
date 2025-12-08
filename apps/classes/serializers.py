from rest_framework import serializers

from apps.booking.serializers import BookingClientSerializer
from apps.classes.models import Classes
from apps.user.serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from zoneinfo import ZoneInfo


class ClassesSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    bookings_count = serializers.IntegerField(read_only=True)
    is_full = serializers.SerializerMethodField()
    bookings = BookingClientSerializer(source="bookings.all", many=True, read_only=True)
    recurrence_type = serializers.SerializerMethodField()
    recurrence_days = serializers.SerializerMethodField()

    def get_is_full(self, obj):
        bookings_count = getattr(obj, "bookings_count", None)
        if bookings_count is None:
            bookings_count = obj.bookings.count()

        return bookings_count >= int(obj.size)

    def get_recurrence_type(self, obj):
        if obj.parent_class:
            return obj.parent_class.recurrence_type
        return obj.recurrence_type

    def get_recurrence_days(self, obj):
        if obj.parent_class:
            return obj.parent_class.recurrence_days
        return obj.recurrence_days

    def to_representation(self, instance):
        data = super().to_representation(instance)

        instructor_timezone = None
        instructor = getattr(instance, "instructor", None)
        if instructor is not None and hasattr(instructor, "account"):
            instructor_timezone = getattr(instructor.account, "timezone", None)

        user_timezone = None

        request = self.context.get("request")

        if request is not None:
            user = getattr(request, "user", None)
            user_account = getattr(user, "account", None)
            user_timezone = getattr(user_account, "timezone", None)

        target_timezone = instructor_timezone or user_timezone

        if instance.date and target_timezone:
            data["date"] = timezone.localtime(
                instance.date, ZoneInfo(target_timezone)
            ).isoformat()

        return data

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
            "parent_class_id"
        ]
