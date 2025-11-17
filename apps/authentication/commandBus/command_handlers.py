from apps.authentication.commandBus.commands import RequestResetPasswordCommand
from .models import PasswordResetToken
from apps.authentication.events.events import SendPasswordResetEvent
from apps.authentication.events.event_dispatchers import auth_event_dispatcher

def handle_request_password_reset(command: RequestResetPasswordCommand):
    user = User.objects.get(email=command.email)

    token = PasswordResetToken.generate_token()
    PasswordResetToken.objects.create(user=user, token=token)

    event = SendPasswordResetEvent(user=user, token=token)
    auth_event_dispatcher.dispatch(event)