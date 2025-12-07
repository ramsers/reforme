import typing
from datetime import datetime


class CreateBookingEvent(typing.NamedTuple):
    booking_id: str

class DeleteBookingEvent(typing.NamedTuple):
    booking_id: str
    client_email: str
    class_title: str
    class_date: datetime
    instructor_name: str | None
    instructor_timezone: str | None
