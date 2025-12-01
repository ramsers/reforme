from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import status, viewsets

from apps.user.filters.user_filters import UserFilter
from apps.user.validators import UpdateUserValidator, CreateUserValidator, DeleteUserValidator
from apps.user.commandBus.commands import UpdateUserCommand, CreateUserCommand, DeleteUserCommand
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

    def get_queryset(self):
        queryset = User.objects.all()
        list_actions = ["list", "all_instructors", "all_clients"]

        if getattr(self, "action", None) in list_actions:
            return queryset.only(
                "id",
                "email",
                "name",
                "phone_number",
                "role",
                "created_at",
            )

        return queryset.prefetch_related("purchases")

    def get_serializer_class(self):
        if getattr(self, "action", None) in ["list", "all_instructors", "all_clients"]:
            return UserListSerializer

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        validator = CreateUserValidator(data={**request.data}, context={"user": request.user})
        validator.is_valid(raise_exception=True)

        command = CreateUserCommand(**validator.validated_data)
        user = user_command_bus.handle(command)

        return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        validator = UpdateUserValidator(data={"id": self.kwargs.get('pk'), **request.data},
                                        context={"user": request.user})
        validator.is_valid(raise_exception=True)

        command = UpdateUserCommand(**validator.validated_data)
        updated_user = user_command_bus.handle(command)

        return Response(data=UserSerializer(updated_user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def me(self, request, *args, **kwargs):
        user = request.user

        return Response(data=UserSerializer(user).data, status=status.HTTP_200_OK)

    @is_admin
    @action(detail=False, methods=["get"], url_path="all-instructors")
    def all_instructors(self, request):
        queryset = User.objects.filter(role=Role.INSTRUCTOR)
        queryset = self.filter_queryset(queryset)
        show_all = request.query_params.get("all") in ["true", "1"]

        if show_all:
            self.paginator.page_size = queryset.count()

        page = self.paginate_queryset(queryset)
        serializer = UserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @is_admin
    @action(detail=False, methods=["get"], url_path="all-clients")
    def all_clients(self, request):
        queryset = User.objects.filter(role=Role.CLIENT)
        queryset = self.filter_queryset(queryset)
        show_all = request.query_params.get("all") in ["true", "1"]

        if show_all:
            self.paginator.page_size = queryset.count()

        page = self.paginate_queryset(queryset)
        serializer = UserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @is_admin
    @action(detail=True, methods=["delete"], url_path="delete")
    def delete(self, request, *args, **kwargs):
        validator = DeleteUserValidator(data={"id": self.kwargs.get('pk')}, context={"user": request.user})
        validator.is_valid(raise_exception=True)

        command = DeleteUserCommand(**validator.validated_data)
        user_command_bus.handle(command)

        return Response(status=status.HTTP_204_NO_CONTENT)