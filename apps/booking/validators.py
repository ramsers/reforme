from rest_framework import serializers
from apps.user.models import User
from apps.user.serializers import UserSerializer
from apps.classes.models import Classes
from apps.booking.models import Booking



class CreateBookingValidator(serializers.Serializer):
    client_id = serializers.UUIDField(required=True, allow_null=False)
    class_id = serializers.UUIDField(required=True, allow_null=False)

    def validate_user_id(self, value):
        booker = self.context.get('booker')
        client = User.objects.get(id=value)

        if client and client.id != booker.id:
            raise serializers.ValidationError("not_allowed")

        return value


class DeleteBookingValidator(serializers.Serializer):
    booking_id = serializers.UUIDField(required=True, allow_null=False)

    def validate_booking_id(self, value):
        booking_to_delete = Booking.objects.get(id=value)

        client = self.context.get('client')

        if booking_to_delete.client.id != client.id:
            raise serializers.ValidationError("not_allowed")

        return value
