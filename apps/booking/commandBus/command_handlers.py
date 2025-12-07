from apps.booking.commandBus.commands import CreateBookingCommand, DeleteBookingCommand
from apps.booking.models import Booking
from apps.booking.events.events import CreateBookingEvent, DeleteBookingEvent
from apps.booking.events.event_dispatchers import booking_event_dispatcher
from apps.booking.selectors.selectors import get_booking_by_id


def handle_create_booking(command: CreateBookingCommand):
    booking: Booking = Booking.objects.create(
        client_id=command.client_id,
        booked_class_id=command.class_id

    )
    event = CreateBookingEvent(booking_id=booking.id)
    booking_event_dispatcher.dispatch(event)

    return booking


def handle_delete_booking(command: DeleteBookingCommand):
    booking: Booking = get_booking_by_id(command.booking_id)

    booked_class = getattr(booking, "booked_class", None)
    instructor = getattr(booked_class, "instructor", None)
    instructor_timezone = getattr(getattr(instructor, "account", None), "timezone", None)

    event = DeleteBookingEvent(
        booking_id=booking.id,
        client_email=booking.client.email,
        class_title=getattr(booked_class, "title", ""),
        class_date=getattr(booked_class, "date", None),
        instructor_name=getattr(instructor, "name", None),
        instructor_timezone=instructor_timezone,
    )
    booking_event_dispatcher.dispatch(event)

    booking.delete()
