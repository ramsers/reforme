import typing

class PaymentSuccessEvent(typing.NamedTuple):
    user_id: str
    product_name: str
