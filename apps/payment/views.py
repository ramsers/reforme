from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe
from rest_framework import status
from apps.payment.commandBus.command_bus import payment_command_bus
from apps.payment.commandBus.commands import (
    CancelSubscriptionCommand,
    CreatePurchaseIntentCommand,
)
from apps.payment.services.webhook_handlers import (
    InvalidPayloadError,
    InvalidSignatureError,
    StripeWebhookHandler,
    WebhookError,
)
import os
from apps.payment.validators import CancelSubscriptionValidator, CreatePurchaseIntentValidator


stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')


class CreatePurchaseIntentApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        validator = CreatePurchaseIntentValidator(data=request.data)
        validator.is_valid(raise_exception=True)

        command = CreatePurchaseIntentCommand(user_id=user.id, **request.data)
        purchase_intent = payment_command_bus.handle(command)

        return Response(data=purchase_intent, status=status.HTTP_200_OK)


class ListProductApi(APIView):
    def get(self, request):
        products = stripe.Product.list(active=True, expand=['data.default_price'])
        result = []

        for product in products.data:
            price = product.default_price
            result.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price_id": price.id if price else None,
                "price_amount": price.unit_amount / 100 if price else None,
                "currency": price.currency if price else None,
                "is_subscription": price.recurring is not None,
                "duration_days": product.metadata.duration_days,
            })


        return Response(data=result, status=status.HTTP_200_OK)


class CancelSubscriptionApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        validator = CancelSubscriptionValidator(data={"purchase_id": pk}, context={"user": request.user})
        validator.is_valid(raise_exception=True)

        print('TEST VALIDATOR ===============', validator.validated_data.get('purchase_id'), flush=True)
        command = CancelSubscriptionCommand(purchase_id=validator.validated_data.get('purchase_id'))
        payment_command_bus.handle(command)

        return Response({"message": "Subscription set to cancel at period end."}, status=status.HTTP_200_OK)


class StripeWebhookApi(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        stripe_webhook_handler = StripeWebhookHandler(
            payload=request.body,
            signature=request.META.get('HTTP_STRIPE_SIGNATURE'),
        )

        try:
            response = stripe_webhook_handler.handle()
        except InvalidSignatureError:
            return Response({"detail": "Invalid Stripe signature."}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidPayloadError:
            return Response({"detail": "Invalid Stripe payload."}, status=status.HTTP_400_BAD_REQUEST)
        except WebhookError:
            return Response({"detail": "Unable to process webhook."}, status=status.HTTP_400_BAD_REQUEST)

        return response
