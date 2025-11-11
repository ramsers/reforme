from rest_framework import serializers
from apps.user.models import User
from apps.user.serializers import UserSerializer
from apps.classes.models import Classes
from apps.booking.models import Booking
from apps.user.value_objects import Role
from django.utils import timezone



class CreateBookingValidator(serializers.Serializer):
    client_id = serializers.UUIDField(required=True, allow_null=False)
    class_id = serializers.UUIDField(required=True, allow_null=False)

    def validate_client_id(self, value):
        booker = self.context.get('booker')
        client = User.objects.get(id=value)

        if client.id != booker.id and booker.role != Role.ADMIN:
            raise serializers.ValidationError("not_allowed")

        return value

    def validate(self, attrs):
        client_id = attrs.get("client_id")
        class_id = attrs.get("class_id")
        booked_class = Classes.objects.get(id=class_id)

        if Booking.objects.filter(client_id=client_id, booked_class_id=class_id).exists():
            raise serializers.ValidationError("already_booked")

        current_bookings = booked_class.bookings.count()
        if current_bookings >= booked_class.size:
            raise serializers.ValidationError("class_full")

        if booked_class.date and booked_class.date < timezone.now():
            raise serializers.ValidationError("class_in_past")

        return attrs


class DeleteBookingValidator(serializers.Serializer):
    booking_id = serializers.UUIDField(required=True, allow_null=False)

    def validate_booking_id(self, value):
        booking_to_delete = Booking.objects.get(id=value)
        print('HITTING Validator ==============', booking_to_delete, flush=True)


        client = self.context.get('client')

        if booking_to_delete.client.id != client.id and client.role != Role.ADMIN:
            raise serializers.ValidationError("not_allowed")

        return value
