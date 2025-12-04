from rest_framework import serializers
from apps.user.models import User
from apps.user.selectors.selectors import get_user_by_id
from apps.user.value_objects import Role
from zoneinfo import ZoneInfo


def validate_iana_timezone(value: str):
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError:
        raise ValidationError("Invalid IANA timezone identifier.")


class CreateUserValidator(serializers.Serializer):
    name = serializers.CharField(required=True, allow_null=False)
    email = serializers.EmailField(required=True, allow_null=False)
    phone_number = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=False, allow_null=True)
    role = serializers.ChoiceField(choices=Role.choices, required=True, allow_null=False)
    timezone = serializers.CharField(
        default="EST",
        validators=[validate_iana_timezone],
    )


    def validate_email(self, value):
        user = self.context.get('user')

        if User.objects.filter(email=value).exclude(email=user.email):
            raise serializers.ValidationError("This email is already in use")
        return value

    def validate(self, attrs):
        user = self.context.get('user')

        if user.role != Role.ADMIN:
            raise serializers.ValidationError("not_allowed")

        return attrs


class UpdateUserValidator(serializers.Serializer):
    id = serializers.UUIDField(required=True, allow_null=False)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=False, allow_null=True, write_only=True)

    def validate_id(self, value):
        user = self.context.get('user')
        user_to_update = get_user_by_id(value)

        if user_to_update.id != user.id and user.role != Role.ADMIN:
            raise serializers.ValidationError("not_allowed")

        self.user_to_update = user_to_update
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        target_user = getattr(self, "user_to_update", None)

        if email and target_user and email != target_user.email:
            if User.objects.filter(email=email).exclude(id=target_user.id).exists():
                raise serializers.ValidationError({"email": "This email is already in use."})

        return attrs


class DeleteUserValidator(serializers.Serializer):
    id = serializers.UUIDField(required=True, allow_null=False)

    def validate_id(self, value):
        user_to_delete = get_user_by_id(value)

        if not user_to_delete:
            raise serializers.ValidationError("user_not_found")

        return value
