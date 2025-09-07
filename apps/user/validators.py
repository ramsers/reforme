from rest_framework import serializers
from apps.user.models import User


class CreateUserValidator(serializers.Serializer):
    name = serializers.CharField(required=True, allow_null=False)
    email = serializers.EmailField(required=True, allow_null=False)
    phone_number = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=True, allow_null=False)

    def validate_email(self, value):
        user = self.context.get('user')

        if User.objects.filter(email=value).exclude(email=user.email):
            raise serializers.ValidationError("This email is already in use")
        return value


class UpdateUserValidator(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=False, allow_null=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        if email:
            user_id = self.context.get("user_id")
            if User.objects.exclude(id=user_id).filter(email=email).exists():
                raise serializers.ValidationError("This email is already in use.")

        return attrs
