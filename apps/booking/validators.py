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

    def validate(self, attrs):
        client_id = attrs.get("client_id")
        class_id = attrs.get("class_id")

        if Booking.objects.filter(client_id=client_id, booked_class_id=class_id).exists():
            raise serializers.ValidationError("already_booked")

        current_bookings = booked_class.bookings.count()
        if current_bookings >= booked_class.size:
            raise serializers.ValidationError("class_full")

        return attrs


class DeleteBookingValidator(serializers.Serializer):
    booking_id = serializers.UUIDField(required=True, allow_null=False)

    def validate_booking_id(self, value):
        booking_to_delete = Booking.objects.get(id=value)

        client = self.context.get('client')

        if booking_to_delete.client.id != client.id:
            raise serializers.ValidationError("not_allowed")

        return value
