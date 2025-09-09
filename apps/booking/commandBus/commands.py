import typing


class CreateBookingCommand(typing.NamedTuple):
    client_id: str
    class_id: str
