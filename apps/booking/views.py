from apps.booking.models import Booking
from rest_framework.decorators import permission_classes, action
from apps.booking.serializers import BookingSerializer
from apps.classes.decorators import is_client
from rest_framework.response import Response
from rest_framework import status, viewsets
from apps.booking.validators import CreateBookingValidator, DeleteBookingValidator
from apps.booking.commandBus.commands import CreateBookingCommand, DeleteBookingCommand
from apps.booking.commandBus.command_bus import booking_command_bus
from rest_framework.permissions import IsAuthenticated
from apps.user.value_objects import Role
from django_filters.rest_framework import DjangoFilterBackend
from apps.booking.filters.booking_filter import BookingFilter


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_queryset(self):
        user = self.request.user

        if user.role == Role.ADMIN:
            return Booking.objects.all()
        elif user.role == Role.INSTRUCTOR:
            return Booking.objects.filter(booked_class__instructor=user)
        else:
            return Booking.objects.filter(client=user)

    def create(self, request, *args, **kwargs):
        validator = CreateBookingValidator(data=request.data, context={"booker": request.user})
        validator.is_valid(raise_exception=True)
        command = CreateBookingCommand(**validator.validated_data)
        booking = booking_command_bus.handle(command)
        serializer = BookingSerializer(booking)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="delete")
    def delete(self, request, *args, **kwargs):
        validator = DeleteBookingValidator(data={'booking_id': self.kwargs.get('pk')}, context={"client": request.user})
        validator.is_valid(raise_exception=True)

        command = DeleteBookingCommand(booking_id=self.kwargs.get('pk'))
        booking = booking_command_bus.handle(command)
        return Response(status=status.HTTP_204_NO_CONTENT)
