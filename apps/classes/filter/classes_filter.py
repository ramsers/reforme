import django_filters
from apps.classes.models import Classes
from django.db.models import Count, Q


class ClassesFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="date", lookup_expr="date")
    start_date = django_filters.DateTimeFilter(field_name="date__date", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="date__date", lookup_expr="lte")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    has_bookings = django_filters.BooleanFilter(method="filter_has_bookings")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Classes
        fields = ["date", "start_date", "end_date", "instructor", "has_bookings"]

    def filter_has_bookings(self, queryset, name, value):
        if value:
            return queryset.annotate(num_bookings=Count("bookings")).filter(num_bookings__gt=0).distinct()
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value) | Q(instructor__name__icontains=value)
        )

    @property
    def qs(self):
        queryset = super().qs
        return queryset.order_by("date")
