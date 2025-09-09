from apps.booking.commandBus.commands import CreateBookingCommand, DeleteBookingCommand
from apps.booking.models import Booking


def handle_create_booking(command: CreateBookingCommand):
    booking: Booking = Booking.objects.create(
        client_id=command.client_id,
        booked_class_id=command.class_id

    )

    return booking


def handle_delete_booking(command: DeleteBookingCommand):
    booking: Booking = Booking.objects.get(id=command.booking_id)
    booking.delete()
