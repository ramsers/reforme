import os
from django.conf import settings
import django_filters
from apps.classes.models import Classes
from django.db.models import Count, Q, F, Value
from django.db.models.functions import Coalesce, TruncDate
from django.db.models import Func


class ClassesFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(method="filter_by_local_date")
    start_date = django_filters.DateFilter(method="filter_by_start_date")
    end_date = django_filters.DateFilter(method="filter_by_end_date")
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

    def _with_local_date(self, queryset):
        default_timezone = os.environ.get("TIME_ZONE", settings.TIME_ZONE)
        timezone_expr = Coalesce(F("instructor__account__timezone"), Value(default_timezone))
        local_time_expr = Func(timezone_expr, F("date"), function="timezone")
        return queryset.annotate(local_date=TruncDate(local_time_expr))

    def filter_by_local_date(self, queryset, name, value):
        if not value:
            return queryset
        queryset = self._with_local_date(queryset)
        return queryset.filter(local_date=value)

    def filter_by_start_date(self, queryset, name, value):
        if not value:
            return queryset
        queryset = self._with_local_date(queryset)
        return queryset.filter(local_date__gte=value)

    def filter_by_end_date(self, queryset, name, value):
        if not value:
            return queryset
        queryset = self._with_local_date(queryset)
        return queryset.filter(local_date__lte=value)

    @property
    def qs(self):
        queryset = super().qs
        return queryset.order_by("date")
