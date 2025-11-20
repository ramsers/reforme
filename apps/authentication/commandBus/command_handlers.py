from apps.authentication.commandBus.commands import RequestResetPasswordCommand, ResetPasswordCommand
from apps.authentication.events.events import SendPasswordResetEvent
from apps.authentication.events.event_dispatchers import auth_event_dispatcher
from apps.authentication.models import PasswordResetToken
from apps.user.selectors import get_user_by_email


def handle_request_password_reset(command: RequestResetPasswordCommand):
    user = get_user_by_email(command.email)

    token = PasswordResetToken.generate_token()
    PasswordResetToken.objects.create(user=user, token=token)

    event = SendPasswordResetEvent(user=user, token=token)
    auth_event_dispatcher.dispatch(event)


def handle_password_reset(command: ResetPasswordCommand):
    user = command.user
    reset_token = command.reset_token

    user.set_password(command.password)
    user.save(update_fields=["password"])

    reset_token.delete()
