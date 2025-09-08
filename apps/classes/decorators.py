from rest_framework.permissions import BasePermission
from apps.user.value_objects import Role
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def is_instructor(function):
    """
    Allows access only to users with role=INSTRUCTOR.
    """
    @wraps(function)
    def decorator(view, request, *args, **kwargs):
        return function(view, request, *args, **kwargs)\
            if request.user.is_authenticated and request.user.role != Role.INSTRUCTOR \
            else Response(status=status.HTTP_403_FORBIDDEN, data="instructors only")
    return decorator


def is_client(function):
    """
    Allows access only to users with role=CLIENT.
    """
    @wraps(function)
    def decorator(view, request, *args, **kwargs):
        return function(view, request, *args, **kwargs)\
            if request.user.is_authenticated and request.user.role != Role.CLIENT\
            else Response(status=status.HTTP_403_FORBIDDEN, data="clients only")
    return decorator
