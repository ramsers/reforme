from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import status, viewsets
from apps.user.validators import UpdateUserValidator, CreateUserValidator
from apps.user.commandBus.commands import UpdateUserCommand, CreateUserCommand
from apps.user.commandBus.command_bus import user_command_bus
from apps.user.serializers import UserSerializer
from apps.user.models import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.classes.decorators import is_admin
from apps.user.value_objects import Role


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        validator = CreateUserValidator(data={**request.data}, context={"user": request.user})
        validator.is_valid(raise_exception=True)

        command = CreateUserCommand(**validator.validated_data)
        user = user_command_bus.handle(command)

        print('USER ======', user)

        return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def me(self, request, *args, **kwargs):
        user = request.user
        # validator = UpdateUserValidator(data=request.data)
        # validator.is_valid(raise_exception=True)
        # command = UpdateUserCommand(user=request.user, **validator.validated_data)
        # updated_user = user_command_bus.handle(command)

        return Response(data=UserSerializer(user).data, status=status.HTTP_200_OK)

    @is_admin
    @action(detail=False, methods=["get"], url_path="all-instructors")
    def all_instructors(self, request):
        users = User.objects.filter(role=Role.INSTRUCTOR)
        print('USERS ===============', users)
        return Response(
            data=UserSerializer(users, many=True).data, status=status.HTTP_200_OK
        )
