from apps.payment.commandBus.commands import (CreatePurchaseIntentCommand, CreatePassPurchaseCommand,
                                              CancelSubscriptionWebhookCommand, CancelSubscriptionCommand)
from apps.user.models import User
import stripe
import os
from apps.payment.models import PassPurchase
from apps.payment.events.event_dispatchers import payment_event_dispatcher
from apps.payment.events.events import PaymentSuccessEvent
from datetime import timedelta
from django.utils import timezone
from apps.payment.events.events import SubscriptionCancellationEvent

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
            success_url=os.environ.get('PAYMENT_REDIRECT'),
            cancel_url=os.environ.get('PAYMENT_REDIRECT'),
            metadata={
                "user_id": user.id,
                "product_name": command.product_name,
                "price_id": command.price_id,
                "duration_days": command.duration_days,
            },
        )

        return checkout_session.url
    else:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(command.price_amount * 100),
            currency=command.currency,
            automatic_payment_methods={"enabled": True},
            metadata={
                "user_id": user.id,
                "product_name": command.product_name,
                "price_id": command.price_id,
                "duration_days": command.duration_days,
            },
        )

        return payment_intent.client_secret

def handle_create_pass_purchase(command: CreatePassPurchaseCommand):
    user = User.objects.get(id=command.user_id)

    if command.stripe_idempotency_key:
        existing_purchase = PassPurchase.objects.filter(
            stripe_idempotency_key=command.stripe_idempotency_key
        ).first()
        if existing_purchase:
            return existing_purchase

    duration_days = int(command.duration_days)

    end_date = timezone.now() + timedelta(days=duration_days) if duration_days > 0 else None

    if command.is_subscription:
        pass_purchase = PassPurchase.objects.create(
            user=user,
            stripe_checkout_id=command.stripe_checkout_id,
            stripe_customer_id=command.stripe_customer_id,
            stripe_price_id=command.stripe_price_id,
            pass_name=command.product_name,
            is_subscription=command.is_subscription,
            stripe_subscription_id=command.stripe_subscription_id,
            active=command.active,
            end_date=end_date,
            stripe_idempotency_key=command.stripe_idempotency_key,
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
            end_date=end_date,
            stripe_idempotency_key=command.stripe_idempotency_key,
        )

    event = PaymentSuccessEvent(user_id=user.id, product_name=command.product_name)
    payment_event_dispatcher.dispatch(event)


    return pass_purchase

def handle_cancel_subscription(command: CancelSubscriptionCommand):
    try:
        purchase = PassPurchase.objects.get(id=command.purchase_id)

        stripe.Subscription.modify(
            purchase.stripe_subscription_id,
            cancel_at_period_end=True,
        )

        purchase.is_cancel_requested = True
        purchase.save(update_fields=["is_cancel_requested"])

        event = SubscriptionCancellationEvent(user_id=purchase.user.id, end_date=purchase.end_date.date())
        payment_event_dispatcher.dispatch(event)
    except PassPurchase.DoesNotExist:
        print({"error": "Purchase not found."}, flush=True)
    except Exception as e:
        print({"error": str(e)}, flush=True)

def handle_update_subscription_cancellation(command: CancelSubscriptionWebhookCommand):
    try:
        purchase = PassPurchase.objects.filter(stripe_subscription_id=command.subscription_id).first()
        if purchase:
            if command.cancel_at_period_end and not purchase.is_cancel_requested:
                purchase.is_cancel_requested = True

            if command.status_stripe == "canceled":
                purchase.is_active = False
                purchase.is_cancel_requested = False

            purchase.save(update_fields=["is_active", "is_cancel_requested"])

    except Exception as e:
        print("❌ Error updating subscription status:", e, flush=True)
