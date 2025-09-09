import typing


class CreateBookingCommand(typing.NamedTuple):
    client_id: str
    class_id: str


class DeleteBookingCommand(typing.NamedTuple):
    booking_id: str
