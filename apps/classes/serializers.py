from rest_framework import serializers

from apps.booking.serializers import BookingClientSerializer
from apps.classes.models import Classes
from apps.user.serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


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

        request = self.context.get("request") if hasattr(self, "context") else None
        user = getattr(request, "user", None) if request else None

        account = None
        if user is not None and hasattr(user, "account"):
            account = user.account

        user_timezone = getattr(account, "timezone", None)
        if instance.date and user_timezone:
            try:
                tzinfo = ZoneInfo(user_timezone)
                class_date = instance.date
                if timezone.is_naive(class_date):
                    class_date = timezone.make_aware(class_date, timezone.get_current_timezone())

                data["date"] = timezone.localtime(class_date, tzinfo).isoformat()
            except ZoneInfoNotFoundError:
                pass

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
