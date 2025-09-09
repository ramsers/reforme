from apps.booking.commandBus.commands import CreateBookingCommand
from apps.booking.models import Booking


def handle_create_booking(command: CreateBookingCommand):
    booking: Booking = Booking.objects.create(
        client_id=command.client_id,
        booked_class_id=command.class_id

    )

    return booking
