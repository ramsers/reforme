import django_filters
from apps.booking.models import Booking


class BookingFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="booked_class__date", lookup_expr="date")
    instructor = django_filters.UUIDFilter(field_name="booked_class__instructor__id")

    class Meta:
        model = Booking
        fields = ["date", "instructor"]
