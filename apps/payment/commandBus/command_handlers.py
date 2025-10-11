from apps.payment.commandBus.commands import CreatePurchaseIntentCommand, CreatePassPurchaseCommand
from apps.user.models import User
import stripe
import os
from apps.payment.models import PassPurchase


def handle_create_purchase_intent(command: CreatePurchaseIntentCommand):
    user = User.objects.get(id=command.user_id)
    if command.is_subscription:

        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=["card"],
            line_items=[{
                "price": command.price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=os.environ.get('FRONTEND_URL'),
            cancel_url=os.environ.get('FRONTEND_URL'),
            metadata={
                "user_id": user.id,
                "product_name": command.product_name,
                "price_id": command.price_id
            },
        )
        print('CHECKING THE SESSION ==============', checkout_session, flush=True)

        return checkout_session.url
    else:
        print('PAYMENT INTENT ==============', command.price_amount, flush=True)
        payment_intent = stripe.PaymentIntent.create(
            amount=int(command.price_amount * 100),
            currency=command.currency,
            automatic_payment_methods={"enabled": True},
            metadata={"user_id": user.id, "product_name": command.product_name, "price_id": command.price_id},
        )

        return payment_intent.client_secret

def handle_create_pass_purchase(command: CreatePassPurchaseCommand):
    print('COMMAND USER ID BRO =====================', command.user_id, flush=True)
    user = User.objects.get(id=command.user_id)

    pass_purchase = None

    if command.is_subscription:
        pass_purchase = PassPurchase.objects.create(
            user=user,
            stripe_checkout_id=command.stripe_checkout_id,
            stripe_customer_id=command.stripe_customer_id,
            stripe_price_id=command.stripe_price_id,
            pass_name=command.product_name,
            is_subscription=command.is_subscription,
            active=command.active,
        )
    else:
        pass_purchase = PassPurchase.objects.create(
            user=user,
            stripe_payment_intent=command.stripe_payment_intent,
            stripe_product_id=command.stripe_product_id,
            pass_name=command.product_name,
            stripe_price_id=command.stripe_price_id,
            is_subscription=command.is_subscription,
            active=command.active,
        )

    return pass_purchase
