from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import status
from apps.user.validators import UpdateUserValidator
from apps.user.commandBus.commands import UpdateUserCommand
from apps.user.commandBus.command_bus import user_command_bus
from apps.user.serializers import UserSerializer
from apps.user.models import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["patch"], url_path="me")
    def me(self, request, *args, **kwargs):
        user = request.user
        validator = UpdateUserValidator(data=request.data)
        validator.is_valid(raise_exception=True)
        command = UpdateUserCommand(user=request.user, **validator.validated_data)
        updated_user = user_command_bus.handle(command)

        return Response(status=status.HTTP_201_CREATED)
