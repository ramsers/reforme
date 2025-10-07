import typing

class CreateBookingEvent(typing.NamedTuple):
    booking__id: str
    user_id: str