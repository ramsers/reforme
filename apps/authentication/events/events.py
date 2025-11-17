import typing
from apps.user.models import User

class UserSignupEvent(typing.NamedTuple):
    user_id: str


class SendPasswordResetEvent(typing.NamedTuple):
    user: User
    token: str