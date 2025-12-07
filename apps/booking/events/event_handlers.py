from apps.booking.events.events import CreateBookingEvent, DeleteBookingEvent
from apps.booking.models import Booking
from apps.core.email_service import send_html_email
from apps.booking.selectors.selectors import get_booking_by_id
from zoneinfo import ZoneInfo

from django.utils import timezone


def handle_send_create_booking_email(event: CreateBookingEvent):
    booking: Booking = get_booking_by_id(event.booking_id)

    class_timezone = _get_instructor_timezone(booking)
    localized_date = timezone.localtime(booking.booked_class.date, class_timezone)
    formatted_date = localized_date.strftime("%A, %B %d at %I:%M %p")

    send_html_email(
        subject=f"Reforme Booking Confirmation for {booking.client.name}",
        to=booking.client.email,
        template_name="emails/booking_confirmation.html",
        context={
            'client_name': booking.client.name,
            'class_name': booking.booked_class.title,
            'class_date': formatted_date,
            'instructor_name': getattr(booking.booked_class.instructor, "name", ""),
        }
    )

def handle_send_delete_booking_email(event: DeleteBookingEvent):
    booking: Booking = get_booking_by_id(event.booking_id)
    class_timezone = _get_instructor_timezone(booking)
    localized_date = timezone.localtime(booking.booked_class.date, class_timezone)
    formatted_date = localized_date.strftime("%A, %B %d at %I:%M %p")

    send_html_email(
        subject=f"Booking cancelled for {booking.booked_class.title}",
        to=booking.client.email,
        template_name="emails/booking_cancelled.html",
        context={
            'class_name': booking.booked_class.title,
            'class_date': formatted_date,
            'instructor_name': getattr(booking.booked_class.instructor, "name", ""),
        }
    )


def _get_instructor_timezone(booking: Booking):
    instructor = booking.booked_class.instructor
    tz_name = getattr(getattr(instructor, "account", None), "timezone", None)
    return ZoneInfo(tz_name) if tz_name else timezone.get_current_timezone()