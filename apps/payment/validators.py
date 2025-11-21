from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from apps.payment.models import PassPurchase


class CreatePurchaseIntentValidator(serializers.Serializer):
    price_id = serializers.CharField(max_length=255)
    product_name = serializers.CharField(max_length=255)
    is_subscription = serializers.BooleanField()
    price_amount = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(max_length=10)
    duration_days = serializers.IntegerField(min_value=1)
    redirect_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True
    )



class CancelSubscriptionValidator(serializers.Serializer):
    purchase_id = serializers.UUIDField(required=True)

    def validate_purchase_id(self, value):
        user = self.context.get("user")

        try:
            purchase = PassPurchase.objects.get(id=value, user=user)
        except PassPurchase.DoesNotExist:
            raise NotFound("Purchase not found.")

        if user and purchase.user_id != user.id:
            raise PermissionDenied("You do not have permission to cancel this purchase.")

        self.purchase = purchase
        return value
