from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.payment.models import PassPurchase
import json
from apps.payment.commandBus.commands import CreatePassPurchaseCommand
from apps.payment.commandBus.command_bus import payment_command_bus
from rest_framework import status
from apps.payment.serializers import ProductSerializer
import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckSessionApi(APIView):
    permission_classes = [IsAuthenticated]

    def create_checkout_session(self, request):
        user = request.user

        command = CreatePassPurchaseCommand(user_id=user.id, **request.data)
        payment_command_bus.handle(command)

        return Response({"status": "success"})

class ListProductApi(APIView):

    def get(self, request):
        products = stripe.Product.list(active=True, expand=['data.default_price'])
        # return Response({"products": products})
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
            })


        return Response(data=result, status=status.HTTP_200_OK)
