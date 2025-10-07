from apps.booking.events.events import CreateBookingEvent
from apps.booking.models import Booking
from apps.core.email_service import send_html_email


def handle_send_create_booking_email(event: CreateBookingEvent):
    booking: Booking = Booking.objects.get(id=event.booking_id)

    print('BOOOKING INSTRUCTOR ==================', booking.booked_class.instructor)

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




    print(f"TEATOBESTO ========= CRESTO DJDJDJDJDJDJDJ ================", booking)