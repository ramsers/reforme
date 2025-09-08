from apps.classes.models import Classes
from rest_framework.decorators import permission_classes, action
from apps.classes.serializers import ClassSerializer
from apps.classes.decorators import IsInstructor, IsClient
from rest_framework.response import Response
from rest_framework import status


class ClassesViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    # serializer

    @permission_classes([IsInstructor])
    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_201_CREATED)
