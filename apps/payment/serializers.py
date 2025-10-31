from rest_framework import serializers
from apps.payment.models import PassPurchase

class ProductSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    id = serializers.CharField()
    unit_amount = serializers.IntegerField()
    currency = serializers.CharField()
    is_subscription = serializers.SerializerMethodField()

    def get_is_subscription(self, obj):
        return True if obj.recurring else False

    class Meta:
        fields = ['id', 'name', 'description', 'id', 'unit_amount', 'currency', 'is_subscription']


class PassPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassPurchase
        fields = [
            'id',
            'stripe_product_id', 'stripe_customer_id', 'pass_name', 'is_subscription', 'is_active',
            'start_date', 'end_date', 'is_cancel_requested'
        ]
