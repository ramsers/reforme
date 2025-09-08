from rest_framework.permissions import BasePermission
from apps.user.value_objects import Role


class IsInstructor(BasePermission):
    """
    Allows access only to users with role=INSTRUCTOR.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.INSTRUCTOR
        )


class IsClient(BasePermission):
    """
    Allows access only to users with role=CLIENT.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.CLIENT
        )
