from apps.classes.models import Classes
from rest_framework.decorators import permission_classes, action
from apps.classes.serializers import ClassesSerializer
from apps.classes.decorators import is_instructor
from rest_framework.response import Response
from rest_framework import status, viewsets
from apps.classes.validators import CreateClassesValidator, PartialUpdateClassesValidator
from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand
from apps.classes.commandBus.command_bus import classes_command_bus
from rest_framework.permissions import IsAuthenticated


class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all()
    serializer = ClassesSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ClassesSerializer(instance)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @is_instructor
    def create(self, request, *args, **kwargs):
        validator = CreateClassesValidator(data=request.data)
        validator.is_valid(raise_exception=True)
        command = CreateClassCommand(**validator.validated_data, instructor_id=request.user.id)
        created_class = classes_command_bus.handle(command)

        serializer = ClassesSerializer(created_class)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @is_instructor
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        validator = PartialUpdateClassesValidator(data={**request.data},
                                                  context={'instructor': request.user, 'class': instance})
        validator.is_valid(raise_exception=True)

        command = PartialUpdateClassCommand(
            id=instance.id,
            name=validator.validated_data.get('name'),
            size=validator.validated_data.get('size'),
            date=validator.validated_data.get('date')
        )

        updated_class = classes_command_bus.handle(command)
        serializer = ClassesSerializer(updated_class)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
