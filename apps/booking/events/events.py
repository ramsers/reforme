import typing

class CreateBookingEvent(typing.NamedTuple):
    booking_id: str

class DeleteBookingEvent(typing.NamedTuple):
    booking_id: str
