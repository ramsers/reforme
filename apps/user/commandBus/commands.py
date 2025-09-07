import typing
from typing import Optional
from apps.user.models import User


class CreateUserCommand(typing.NamedTuple):
    name: str
    email: str
    password: str
    phone_number: str | None = None


class UpdateUserCommand(typing.NamedTuple):
    user: User
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    password: str | None = None
