import typing
from typing import Optional
from apps.user.models import User
from datetime import timedelta, datetime


class CreateClassCommand(typing.NamedTuple):
    title: str
    description: str
    size: int
    date: datetime
    instructor_id: str


class PartialUpdateClassCommand(typing.NamedTuple):
    id: str
    title: str | None = None
    description: str | None = None
    size: int | None = None
    date: datetime | None = None
