import typing
from typing import Optional
from apps.user.value_objects import Role


class CreateUserCommand(typing.NamedTuple):
    name: str
    email: str
    password: str | None = None
    phone_number: str | None = None
    role: Role | None = None


class UpdateUserCommand(typing.NamedTuple):
    id: str
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    password: str | None = None
    role: Role | None = None


class DeleteUserCommand(typing.NamedTuple):
    id: str