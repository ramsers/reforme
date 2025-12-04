from rest_framework import serializers
from apps.user.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from apps.user.selectors.selectors import get_user_by_email
from apps.user.value_objects import Role
from apps.authentication.models import PasswordResetToken
from django.utils import timezone
from apps.user.validators import validate_iana_timezone


class SignUpValidator(serializers.Serializer):
    name = serializers.CharField(required=True, allow_null=False)
    email = serializers.EmailField(required=True, allow_null=False)
    phone_number = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=True, allow_null=False)
    role = serializers.ChoiceField(choices=Role.choices, required=False, allow_null=True)
    timezone = serializers.CharField(
        # required=True,
        # allow_null=False,
        default="EST",
        validators=[validate_iana_timezone],
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("This email and password are required")

        if User.objects.filter(email=email):
            raise serializers.ValidationError("This email is already in use")

        return attrs


class LoginValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_null=False)
    password = serializers.CharField(required=True, allow_null=False, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")


        user = get_user_by_email(email)
        if not user:
            raise serializers.ValidationError("User not found")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Password doesn't match")

        attrs["user"] = user
        return attrs


class ForgotPasswordValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_null=False)

    def validate_email(self, value):
        user = get_user_by_email(value)

        if not user:
            raise serializers.ValidationError("If email exists, a reset link will be sent.")
        return value


class ResetPasswordValidator(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        token = attrs.get("token")

        try:
            reset_token = PasswordResetToken.objects.select_related("user").get(token=token)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("invalid_token")

        if reset_token.is_expired():
            reset_token.delete()
            raise serializers.ValidationError("token_expired")

        attrs["user"] = reset_token.user
        attrs["reset_token"] = reset_token

        return attrs
