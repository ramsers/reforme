from .events import BookingCreatedEvent

def handle_send_create_booking_email(event: BookingCreatedEvent):
    # For example: send confirmation email, log activity, etc.
    print(f"Booking created for user {event.user_id} with id {event.booking_id}")