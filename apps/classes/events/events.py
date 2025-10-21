import typing

class RescheduleClassEvent(typing.NamedTuple):
    class_id: str
    update_series: bool
    new_date: datetime