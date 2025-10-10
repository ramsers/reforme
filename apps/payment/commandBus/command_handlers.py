from apps.payment.commandBus.commands import CreatePassPurchaseCommand
from apps.user.models import User
import stripe
import os


def handle_create_pass_purchase(command: CreatePassPurchaseCommand):
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
            metadata={"user_id": user.id, "product_name": command.product_name},
        )


        return payment_intent.client_secret
