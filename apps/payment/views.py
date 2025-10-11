from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.payment.models import PassPurchase
import json
from apps.payment.commandBus.commands import CreatePurchaseIntentCommand
from apps.payment.commandBus.command_bus import payment_command_bus
from rest_framework import status
from apps.payment.serializers import PassPurchaseSerializer
import stripe
from django.conf import settings
import os
from apps.payment.commandBus.commands import CreatePassPurchaseCommand


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePurchaseIntentApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

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


class StripeWebhookAPI(APIView):
    def post(self, request):
        payload = request.body
        signature_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        event = None
        pass_purchase = None

        try:
            event = stripe.Webhook.construct_event(payload, signature_header, endpoint_secret)
        except ValueError:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        object_data = event["data"]["object"]

        metadata = object_data.get("metadata", {})  # metadata dict
        is_subscription = event["type"] == "checkout.session.completed"
        print('HITTING HERE =======================', object_data, flush=True)


        if event['type'] == 'payment_intent.succeeded' or event['type'] == 'checkout.session.completed':
            print('HITTING INTO CREATE PASS COMMAND ==============================', metadata, flush=True)
            command = CreatePassPurchaseCommand(
                user_id=metadata.get("user_id"),
                product_name=metadata.get("product_name"),
                is_subscription=is_subscription,
                stripe_checkout_id=object_data["id"] if is_subscription else None,
                stripe_payment_intent=object_data["id"] if not is_subscription else None,
                stripe_price_id=metadata.get("price_id"),
                stripe_product_id=metadata.get("product_id"),
                stripe_customer_id=object_data.get("customer") if is_subscription else None,
                duration_days= metadata.get("duration_days"),
                active=True
            )

            pass_purchase = payment_command_bus.handle(command)
            serializer = PassPurchaseSerializer(pass_purchase)

            print('SERIALIZER =============', serializer.data, flush=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)