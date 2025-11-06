import typing

class PaymentSuccessEvent(typing.NamedTuple):
    user_id: str
    product_name: str


class SubscriptionCancellationEvent(typing.NamedTuple):
    user_id: str
    end_date: str
