from apps.booking.events.events import CreateBookingEvent, DeleteBookingEvent
from apps.booking.models import Booking
from apps.core.email_service import send_html_email


def handle_send_create_booking_email(event: CreateBookingEvent):
    booking: Booking = Booking.objects.get(id=event.booking_id)

    send_html_email(
        subject=f"Reforme Booking Confirmation for {booking.client.name}",
        to=booking.client.email,
        template_name="emails/booking_confirmation.html",
        context={
            'client_name': booking.client.name,
            'class_name': booking.booked_class.title,
            'class_date': booking.booked_class.date,
            'instructor_name': booking.booked_class.instructor,
        }
    )

def handle_send_delete_booking_email(event: DeleteBookingEvent):
    booking: Booking = Booking.objects.get(id=event.booking_id)

    print('TEST HITTING EVENT HANDLER ========================', flush=True)

    send_html_email(
        subject=f"Booking cancelled for {booking.booked_class.title}",
        to=booking.client.email,
        template_name="emails/booking_cancelled.html",
        context={
            'class_name': booking.booked_class.title,
            'class_date': booking.booked_class.date,
            'instructor_name': booking.booked_class.instructor,
        }
    )
