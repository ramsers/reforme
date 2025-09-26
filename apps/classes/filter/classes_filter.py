import django_filters
from apps.classes.models import Classes
from django.db.models import Count


class ClassesFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="date", lookup_expr="date")

    start_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="lte")

    has_bookings = django_filters.BooleanFilter(method="filter_has_bookings")

    class Meta:
        model = Classes
        fields = ["date", "start_date", "end_date", "instructor", "has_bookings"]

    def filter_has_bookings(self, queryset, name, value):
        if value:
            return queryset.annotate(num_bookings=Count("bookings")).filter(num_bookings__gt=0)
        return queryset
