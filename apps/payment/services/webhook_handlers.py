import logging
import os
from typing import Any, Dict, Optional

import stripe
from rest_framework import status
from rest_framework.response import Response

from apps.payment.commandBus.command_bus import payment_command_bus
from apps.payment.commandBus.commands import (
    CancelSubscriptionWebhookCommand,
    CreatePassPurchaseCommand,
)
from apps.payment.serializers import PassPurchaseSerializer


logger = logging.getLogger(__name__)


class WebhookError(Exception):
    """Base exception for webhook errors."""


class InvalidPayloadError(WebhookError):
    """Raised when the webhook payload cannot be parsed."""


class InvalidSignatureError(WebhookError):
    """Raised when the webhook signature validation fails."""


class StripeWebhookHandler:
    """Process Stripe webhook events and dispatch commands."""

    def __init__(
        self,
        payload: bytes,
        signature: Optional[str],
        endpoint_secret: Optional[str] = None,
    ) -> None:
        self.payload = payload
        self.signature = signature
        self.endpoint_secret = endpoint_secret or os.environ.get("STRIPE_WEBHOOK_SECRET")

    def parse_event(self) -> Dict[str, Any]:
        if not self.signature or not self.endpoint_secret:
            logger.error("Missing Stripe signature or endpoint secret for webhook handling.")
            raise InvalidSignatureError("Missing signature or endpoint secret.")

        try:
            return stripe.Webhook.construct_event(
                self.payload,
                self.signature,
                self.endpoint_secret,
            )
        except ValueError as exc:
            logger.exception("Invalid Stripe webhook payload.")
            raise InvalidPayloadError("Invalid payload.") from exc
        except stripe.error.SignatureVerificationError as exc:  # type: ignore[attr-defined]
            logger.exception("Stripe webhook signature verification failed.")
            raise InvalidSignatureError("Invalid signature.") from exc

    def handle(self) -> Response:
        event = self.parse_event()
        event_type = event.get("type")
        logger.info("Processing Stripe webhook event: %s", event_type)

        data_object = event.get("data", {}).get("object", {})
        metadata = data_object.get("metadata", {})

        if event_type in ("payment_intent.succeeded", "checkout.session.completed"):
            is_subscription = event_type == "checkout.session.completed"
            idempotency_key = metadata.get("event_id") or event.get("id")

            if data_object and metadata:
                command = CreatePassPurchaseCommand(
                    user_id=metadata.get("user_id"),
                    product_name=metadata.get("product_name"),
                    is_subscription=is_subscription,
                    stripe_checkout_id=data_object.get("id") if is_subscription else None,
                    stripe_payment_intent=data_object.get("id") if not is_subscription else None,
                    stripe_price_id=metadata.get("price_id"),
                    stripe_product_id=metadata.get("product_id"),
                    stripe_customer_id=data_object.get("customer") if is_subscription else None,
                    stripe_subscription_id=data_object.get("subscription") if is_subscription else None,
                    duration_days=metadata.get("duration_days", 0),
                    active=True,
                    stripe_idempotency_key=idempotency_key,
                )

                pass_purchase = payment_command_bus.handle(command)
                serializer = PassPurchaseSerializer(pass_purchase)
                return Response(serializer.data, status=status.HTTP_200_OK)

        if event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
            subscription_id = data_object.get("id") or data_object.get("subscription")
            command = CancelSubscriptionWebhookCommand(
                subscription_id=subscription_id,
                status_stripe=data_object.get("status"),
                cancel_at_period_end=data_object.get("cancel_at_period_end", False),
            )
            payment_command_bus.handle(command)
            return Response(status=status.HTTP_200_OK)

        logger.info("Unhandled Stripe webhook event type: %s", event_type)
        return Response(status=status.HTTP_200_OK)