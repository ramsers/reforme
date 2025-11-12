from apps.classes.models import Classes
from rest_framework.decorators import permission_classes, action
from apps.classes.serializers import ClassesSerializer
from apps.classes.decorators import is_instructor, is_admin
from rest_framework.response import Response
from rest_framework import status, viewsets
from apps.classes.validators import CreateClassesValidator, PartialUpdateClassesValidator
from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand, DeleteClassCommand
from apps.classes.commandBus.command_bus import classes_command_bus
from rest_framework.permissions import IsAuthenticated
from apps.classes.filter.classes_filter import ClassesFilter
from django_filters.rest_framework import DjangoFilterBackend


class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all()
    serializer_class = ClassesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClassesFilter
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'role') and user.role == "INSTRUCTOR":
            return Classes.objects.filter(instructor=user)
        else:
            return Classes.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ClassesSerializer(instance)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @is_admin
    def create(self, request, *args, **kwargs):
        validator = CreateClassesValidator(data=request.data)
        validator.is_valid(raise_exception=True)
        command = CreateClassCommand(**validator.validated_data)
        created_class = classes_command_bus.handle(command)

        serializer = ClassesSerializer(created_class)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @is_admin
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        print('TEST REQUEST DATA ==========', request.data, flush=True)

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
        )

        updated_class = classes_command_bus.handle(command)
        serializer = ClassesSerializer(updated_class)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @is_admin
    @action(detail=True, methods=["delete"], url_path="delete")
    def delete(self, request, *args, **kwargs):
        print('TESTO BESTO ===================', self.kwargs.get('pk'), flush=True)
        command = DeleteClassCommand(id=self.kwargs.get('pk'),
                                     delete_series=request.GET.get('delete_series') == 'true')
        classes_command_bus.handle(command)

        return Response(status=status.HTTP_204_NO_CONTENT)