from apps.booking.commandBus.commands import CreateBookingCommand, DeleteBookingCommand
from apps.booking.models import Booking
from apps.booking.events.events import CreateBookingEvent, DeleteBookingEvent
from apps.booking.events.event_dispatchers import booking_event_dispatcher


def handle_create_booking(command: CreateBookingCommand):
    booking: Booking = Booking.objects.create(
        client_id=command.client_id,
        booked_class_id=command.class_id

    )
    event = CreateBookingEvent(booking_id=booking.id)
    booking_event_dispatcher.dispatch(event)

    return booking


def handle_delete_booking(command: DeleteBookingCommand):
    booking: Booking = Booking.objects.get(id=command.booking_id)
    event = DeleteBookingEvent(booking_id=booking.id)
    booking_event_dispatcher.dispatch(event)

    booking.delete()
