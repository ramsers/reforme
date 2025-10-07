from apps.authentication.events.events import UserSignupEvent
from apps.user.models import User
from apps.core.email_service import send_html_email


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