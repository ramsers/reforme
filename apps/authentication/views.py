from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.validators import SignUpValidator, LoginValidator
from apps.user.commandBus.command_bus import user_command_bus
from apps.user.commandBus.commands import CreateUserCommand
from apps.user.serializers import UserSerializer


class SignUpAPI(APIView):
    def post(self, request, *args, **kwargs):
        validator = SignUpValidator(data={**request.data})
        validator.is_valid(raise_exception=True)

        with transaction.atomic():
            user_command = CreateUserCommand(**validator.validated_data)
        user = user_command_bus.handle(user_command)
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)

        return Response(
            {
                "user": serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPI(APIView):
    def post(self, request, *args, **kwargs):
        validator = LoginValidator(data={**request.data})
        validator.is_valid(raise_exception=True)

        user = validator.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)

        return Response(
            {
                "user": serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
