from apps.authentication.events.events import UserSignupEvent, SendPasswordResetEvent
from apps.user.models import User
from apps.core.email_service import send_html_email
import os


def handle_send_sign_up_email(event: UserSignupEvent):
    user: User = User.objects.get(id=event.user_id)

    send_html_email(
        subject=f"Welcome to Reforme {user.name}",
        to=user.email,
        template_name="emails/sign_up_confirmation.html",
        context={
            'client_name': user.name,
        }
    )


def handle_send_password_reset_email(event: SendPasswordResetEvent):
    user = event.user
    token = event.token
    reset_url = f"{os.environ.get('FRONTEND_URL')}/authenticate/reset-password?token={token}"

    send_html_email(
        subject="Reset Your Reforme Password",
        to=user.email,
        template_name="emails/password_reset.html",
        context={
            "client_name": user.name,
            "reset_url": reset_url
        }
    )