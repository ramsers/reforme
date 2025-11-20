from apps.payment.models import PassPurchase


def get_pass_purchase_by_id(purchase_id):
    try:
        pass_purchase = PassPurchase.objects.get(id=purchase_id)
    except PassPurchase.DoesNotExist:
        return None
    return pass_purchase