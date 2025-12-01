from rest_framework import serializers
from apps.user.models import User
from apps.payment.serializers import PassPurchaseSerializer


class UserSerializer(serializers.ModelSerializer):
    purchases = PassPurchaseSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'created_at',
            'email',
            'id',
            'name',
            'phone_number',
            'password',
            'role',
            'purchases'
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'created_at',
            'email',
            'id',
            'name',
            'phone_number',
            'role',
        ]