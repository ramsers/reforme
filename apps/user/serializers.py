from rest_framework import serializers
from apps.user.models import User
from apps.payment.serializers import PassPurchaseSerializer
from apps.user.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["bio", "timezone"]


class UserSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    purchases = PassPurchaseSerializer(many=True, read_only=True)

    def get_account(self, obj):
        return AccountSerializer(obj.account, context=self.context).data

    class Meta:
        model = User
        fields = [
            'created_at',
            'account',
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
            'account'
        ]