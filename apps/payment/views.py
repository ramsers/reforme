from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.payment.models import PassPurchase
import json
from apps.payment.commandBus.commands import CreatePassPurchaseCommand
from apps.payment.commandBus.command_bus import payment_command_bus
from rest_framework import status


class CreateCheckSessionApi(APIView):
    permission_classes = [IsAuthenticated]

    def create_checkout_session(self, request):
        user = request.user

        command = CreatePassPurchaseCommand(user_id=user.id, **request.data)
        payment_command_bus.handle(command)

        return Response({"status": "success"})



