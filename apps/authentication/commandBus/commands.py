import typing
from apps.user.models import User
from apps.authentication.models import PasswordResetToken

class RequestResetPasswordCommand(typing.NamedTuple):
    email: str


class ResetPasswordCommand(typing.NamedTuple):
    user: User
    password: str
    reset_token: PasswordResetToken