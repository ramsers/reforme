from apps.payment.commandBus.commands import CreatePassPurchaseCommand
from apps.user.models import User
import stripe
import os


def handle_create_pass_purchase(command: CreatePassPurchaseCommand):
    user = User.objects.get(id=command.user_id)
    # print('Im hitting purchase command ===========', user)
    checkout_session = ''
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=["card"],
            line_items=[{
                "price": command.price_id,
                "quantity": 1,
            }],
            mode="subscription" if command.is_subscription else "payment",
            success_url=os.environ.get('FRONTEND_URL'),
            cancel_url=os.environ.get('FRONTEND_URL'),
            metadata={
                "user_id": user.id,
                "product_name": command.product_name,
            },
        )
        print('CHECKING THE SESSION ==============', checkout_session, flush=True)

        return checkout_session.id
    except Exception as e:
        print('MOLO GOLO SHOLO', e)

    print('Im hitting purchase command ===========', checkout_session, flush=True)
    # checkout_session = ''

    # return checkout_session.id
