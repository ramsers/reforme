from apps.classes.models import Classes
from rest_framework.decorators import permission_classes, action
from apps.classes.serializers import ClassesSerializer
from apps.classes.decorators import is_admin
from rest_framework.response import Response
from rest_framework import status, viewsets
from apps.classes.validators import CreateClassesValidator, PartialUpdateClassesValidator
from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand, DeleteClassCommand
from apps.classes.commandBus.command_bus import classes_command_bus
from rest_framework.permissions import IsAuthenticated
from apps.classes.filter.classes_filter import ClassesFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Prefetch
from apps.booking.models import Booking



class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all()
    serializer_class = ClassesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClassesFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.setdefault("request", self.request)
        return context

    def get_queryset(self):
        bookings_prefetch = Prefetch(
            "bookings",
            queryset=Booking.objects.select_related("client").order_by("created_at"),
        )

        queryset = (
            Classes.objects.select_related("instructor", "parent_class")
            .prefetch_related(bookings_prefetch, "bookings__client")
            .annotate(bookings_count=Count("bookings"))
        )

        user = self.request.user
        if hasattr(user, 'role') and user.role == "INSTRUCTOR":
            queryset = queryset.filter(instructor=user)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @is_admin
    def create(self, request, *args, **kwargs):
        print('TESTO VIEW =================', request.data, flush=True)

        validator = CreateClassesValidator(data=request.data)
        validator.is_valid(raise_exception=True)
        print('TESTO validator =================', validator.validated_data.get('date'), flush=True)

        command = CreateClassCommand(**validator.validated_data)
        created_class = classes_command_bus.handle(command)

        serializer = self.get_serializer(created_class)
        print('TESTO VIEW =================', serializer.data, flush=True)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @is_admin
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        validator = PartialUpdateClassesValidator(data={**request.data},
                                                  context={'user': request.user, 'class': instance})
        validator.is_valid(raise_exception=True)

        command = PartialUpdateClassCommand(
            id=instance.id,
            title=validator.validated_data.get('title'),
            description=validator.validated_data.get('description'),
            size=validator.validated_data.get('size'),
            date=validator.validated_data.get('date'),
            recurrence_type=validator.validated_data.get('recurrence_type'),
            recurrence_days=validator.validated_data.get('recurrence_days'),
            update_series=request.data.get('update_series'),
            instructor_id=validator.validated_data.get('instructor_id'),
        )

        updated_class = classes_command_bus.handle(command)
        serializer = self.get_serializer(updated_class)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @is_admin
    @action(detail=True, methods=["delete"], url_path="delete")
    def delete(self, request, *args, **kwargs):
        command = DeleteClassCommand(id=self.kwargs.get('pk'),
                                     delete_series=request.GET.get('delete_series') == 'true')
        classes_command_bus.handle(command)

        return Response(status=status.HTTP_204_NO_CONTENT)