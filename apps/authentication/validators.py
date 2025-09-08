from rest_framework import serializers
from apps.user.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from apps.user.value_objects import Role


class SignUpValidator(serializers.Serializer):
    name = serializers.CharField(required=True, allow_null=False)
    email = serializers.EmailField(required=True, allow_null=False)
    phone_number = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=True, allow_null=False)
    role = serializers.ChoiceField(choices=Role.choices, required=False, allow_null=True)

    def validate(self, attrs):
        user = self.context.get('user')
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

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid credentials.")

        attrs["user"] = user
        return attrs
