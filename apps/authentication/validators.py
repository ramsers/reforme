from rest_framework import serializers


class SignUpValidator(serializers.Serializer):
    name = serializers.CharField(required=True, allow_null=False)
    email = serializers.EmailFields(required=True, allow_null=False)
    phone_number = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=True, allow_null=False)

    def validate_email(self, value):
        user = self.context.get('user')

        if User.objects.filter(email=value).exclude(email=user.email):
            raise serializers.ValidationError("This email is already in use")
        return value
