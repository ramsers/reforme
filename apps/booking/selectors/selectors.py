from apps.booking.models import Booking


def get_booking_by_id(id: str):
    try:
        booking: Booking = Booking.objects.get(id=id)
    except Booking.DoesNotExist:
        return None
    return booking