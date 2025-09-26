from rest_framework import serializers
from apps.classes.models import Classes
from apps.user.serializers import UserSerializer
from apps.user.models import User
from django.core.exceptions import ObjectDoesNotExist


class ClassesSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()
    bookings_count = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    bookers = serializers.SerializerMethodField()

    def get_instructor(self, obj):
        try:
            return UserSerializer(obj.instructor).data
        except ObjectDoesNotExist:
            return None

    def get_bookings_count(self, obj):
        return obj.bookings.count()

    def get_is_full(self, obj):
        return obj.bookings.count() >= obj.size

    def get_bookers(self, obj):
        clients = User.objects.filter(booked_class__booked_class=obj)

        return UserSerializer(clients, many=True).data

    class Meta:
        model = Classes
        fields = [
            "title",
            "description",
            "size",
            "length",
            "date",
            "instructor",
            "bookings_count",
            "is_full",
            "bookers",
        ]
