from apps.booking.models import Booking


def get_booking_by_id(id: str):
    try:
        booking: Booking = Booking.objects.get(id=id)
    except Booking.DoesNotExist:
        print(f"Booking with id {event.booking_id} not found. Skipping confirmation email.", flush=True)
        return None
    return booking