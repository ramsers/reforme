from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import status


class UserViewSet(ModelViewSet):

    def create(self, request,  *args, **kwargs):
        print('TEST ENDPOINT =======', request.data, flush=True)
        return Response(status=status.HTTP_201_CREATED)
