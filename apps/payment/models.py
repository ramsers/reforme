from django.db import models
from django.conf import settings

class PassPurchase(UUIDModel, TimestampModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    stripe_checkout_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    pass_name = models.CharField(max_length=255)
    is_subscription = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)


    class Meta:
        ordering = ['-created_at']
        db_table = "pass_purchases"