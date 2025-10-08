import typing

class CreatePassPurchaseCommand(typing.NamedTuple):
    user_id: str
    price_id: str
    product_name: str
    is_subscription: bool