from rest_framework import serializers
from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        ordering = ['-created_at']
        fields = [
            'email',
            'id',
            'name',
            'phone_number',
            'password',
            'role'
        ]
