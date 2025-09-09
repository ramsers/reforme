from rest_framework import serializers
from apps.user.models import User
from apps.user.serializers import UserSerializer


class CreateBookingValidator(serializers.Serializer):
    client_id = serializers.UUIDField(required=True, allow_null=False)
    class_id = serializers.UUIDField(required=True, allow_null=False)

    def validate_user_id(self, value):
        booker = self.context.get('booker')
        client = User.objects.get(id=value)

        if client and client.id != booker.id:
            raise serializers.ValidationError("not_allowed")

        return value
