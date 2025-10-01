from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import status, viewsets

from apps.user.filters.user_filters import UserFilter
from apps.user.validators import UpdateUserValidator, CreateUserValidator
from apps.user.commandBus.commands import UpdateUserCommand, CreateUserCommand
from apps.user.commandBus.command_bus import user_command_bus
from apps.user.serializers import UserSerializer
from apps.user.models import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.classes.decorators import is_admin
from apps.user.value_objects import Role
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    pagination_class = UserPagination

    def create(self, request, *args, **kwargs):
        validator = CreateUserValidator(data={**request.data}, context={"user": request.user})
        validator.is_valid(raise_exception=True)

        print('VALIDATOR ================', validator.validated_data, flush=True)

        command = CreateUserCommand(**validator.validated_data)
        user = user_command_bus.handle(command)

        print('USER ======', user)

        return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        validator = UpdateUserValidator(data={**request.data}, context={"user": request.user})
        validator.is_valid(raise_exception=True)

        command = UpdateUserCommand(**validator.validated_data)
        user = user_command_bus.handle(command)

        return Response(data=UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def me(self, request, *args, **kwargs):
        user = request.user

        return Response(data=UserSerializer(user).data, status=status.HTTP_200_OK)

    @is_admin
    @action(detail=False, methods=["get"], url_path="all-instructors")
    def all_instructors(self, request):
        queryset = User.objects.filter(role=Role.INSTRUCTOR)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @is_admin
    @action(detail=False, methods=["get"], url_path="all-clients")
    def all_clients(self, request):
        queryset = User.objects.filter(role=Role.CLIENT)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        validator = UpdateUserValidator(data={"id": self.kwargs.get('pk'), **request.data})
        validator.is_valid(raise_exception=True)
        command = UpdateUserCommand(**validator.validated_data)
        updated_user = user_command_bus.handle(command)

        return Response(data=UserSerializer(updated_user).data, status=status.HTTP_200_OK)