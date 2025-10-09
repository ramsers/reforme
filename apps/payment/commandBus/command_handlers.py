from apps.payment.commandBus.commands import CreatePassPurchaseCommand

def handle_create_pass_purchase(command: CreatePassPurchaseCommand):
    user = User.objects.get(id=command.user_id)
    print('Im hitting purchase command ===========', user)

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=["card"],
            line_items=[{
                "price": command.price_id,
                "quantity": 1,
            }],
            mode="subscription" if command.is_subscription else "payment",
            # success_url=settings.FRONTEND_URL + "/success",
            # cancel_url=settings.FRONTEND_URL + "/cancel",
            metadata={
                "user_id": user.id,
                "product_name": command.product_name,
            },
        )
    except Exception as e:
        print('MOLO GOLO SHOLO', e)

    return checkout_session.id