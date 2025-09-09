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


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        validator = CreateBookingValidator(data=request.data)
        validator.is_valid(raise_exception=True)
        command = CreateBookingCommand(**validator.validated_data)
        booking = booking_command_bus.handle(command)
        serializer = BookingSerializer(booking)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="delete")
    def delete(self, request, *args, **kwargs):
        validator = DeleteBookingValidator(data={'class_id': self.kwargs.get('pk')}, context={"client": request.user})
        validator.is_valid(raise_exception=True)

        command = DeleteBookingCommand(booking_id=self.kwargs.get('pk'))
        booking = booking_command_bus.handle(command)
        return Response(status=status.HTTP_204_NO_CONTENT)
