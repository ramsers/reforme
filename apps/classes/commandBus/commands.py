import typing
from typing import Optional
from datetime import timedelta, datetime
from typing import List, Optional


class CreateClassCommand(typing.NamedTuple):
    title: str
    description: str
    size: int
    date: datetime
    instructor_id: str | None = None
    recurrence_type: Optional[str] = None
    recurrence_days: Optional[List[int]] = None


class PartialUpdateClassCommand(typing.NamedTuple):
    id: str
    title: str | None = None
    description: str | None = None
    size: int | None = None
    date: datetime | None = None
    instructor_id: str | None = None
    recurrence_type: Optional[str] = None
    recurrence_days: Optional[List[int]] = None
    update_series: bool = False


class DeleteClassCommand(typing.NamedTuple):
    id: str
    delete_series: bool = False

