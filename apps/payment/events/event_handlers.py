from apps.payment.events.events import PaymentSuccessEvent, SubscriptionCancellationEvent
from apps.user.models import User
from apps.core.email_service import send_html_email


def send_payment_success_email(event: PaymentSuccessEvent):
    user: User = User.objects.get(id=event.user_id)

    send_html_email(
        subject="Purchase successful!",
        to=user.email,
        template_name="emails/payment_success.html",
        context={
            'pass_name': event.product_name,
            'client_name': user.name,
        }
    )


def send_subscription_cancelled_email(event: SubscriptionCancellationEvent):
    user: User = User.objects.get(id=event.user_id)

    send_html_email(
        subject="Subscription canceled!",
        to=user.email,
        template_name="emails/subscription_cancelled.html",
        context={
            'name': user.name,
            'end_date': user.name,
        }
    )
