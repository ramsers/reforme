import typing

class CreatePurchaseIntentCommand(typing.NamedTuple):
    user_id: str
    price_id: str
    product_name: str
    is_subscription: bool
    price_amount: int
    currency: str


class CreatePassPurchaseCommand(typing.NamedTuple):
    user_id: str
    stripe_product_id: str
    product_name: str
    stripe_price_id: str
    is_subscription: bool
    active: bool
    stripe_product_id: str
    stripe_payment_intent: str | None = None
    stripe_checkout_id: str | None = None
    stripe_customer_id: str | None = None
