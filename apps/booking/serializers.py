from rest_framework import serializers
from apps.user.serializers import UserSerializer
from apps.booking.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    booked_class = serializers.SerializerMethodField()

    def get_client(self, value):
        client = value.client

        return UserSerializer(client, context=self.context).data

    def get_booked_class(self, value):
        from apps.classes.serializers import ClassesSerializer

        booking = value.booked_class

        return ClassesSerializer(booking, context=self.context).data

    class Meta:
        model = Booking
        fields = "__all__"

class BookingClientSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    client = UserSerializer()

    class Meta:
        model = Booking
        fields = "__all__"
