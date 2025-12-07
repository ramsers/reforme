from django.conf import settings
import django_filters
from apps.classes.models import Classes
from django.db.models import Count, Q, F, Value, DateTimeField
from django.db.models.functions import Coalesce, TruncDate
from django.db.models import Func
import pytz
from datetime import datetime, time


class ClassesFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(method="filter_by_date")
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
    #
    # def _with_local_date(self, queryset):
    #     default_timezone = settings.TIME_ZONE
    #     timezone_expr = Coalesce(F("instructor__account__timezone"), Value(default_timezone))
    #     local_time_expr = Func(
    #         timezone_expr, F("date"), function="timezone", output_field=DateTimeField()
    #     )
    #     return queryset.annotate(local_date=TruncDate(local_time_expr))
    #
    # def filter_by_local_date(self, queryset, name, value):
    #     if not value:
    #         return queryset
    #     queryset = self._with_local_date(queryset)
    #     return queryset.filter(local_date=value)

    # def filter_by_start_date(self, queryset, name, value):
    #     if not value:
    #         return queryset
    #     queryset = self._with_local_date(queryset)
    #     return queryset.filter(local_date__gte=value)
    #
    # def filter_by_end_date(self, queryset, name, value):
    #     if not value:
    #         return queryset
    #     queryset = self._with_local_date(queryset)
    #     return queryset.filter(local_date__lte=value)

    def _get_timezone(self):
        return (
            self.request.user.account.timezone
            if hasattr(self.request.user, "account")
            else settings.TIME_ZONE
        )

    def _local_day_range(self, value):
        """
        Convert a local (instructor) date to UTC start and end datetimes.
        """
        tz = pytz.timezone(self._get_timezone())
        # value is a date (YYYY-MM-DD)
        local_start = tz.localize(datetime.combine(value, time.min))
        local_end = tz.localize(datetime.combine(value, time.max))

        return local_start.astimezone(pytz.utc), local_end.astimezone(pytz.utc)

    def filter_by_date(self, queryset, name, value):
        if not value:
            return queryset

        utc_start, utc_end = self._local_day_range(value)
        return queryset.filter(date__gte=utc_start, date__lte=utc_end)

    def filter_by_start_date(self, queryset, name, value):
        if not value:
            return queryset

        utc_start, _ = self._local_day_range(value)
        return queryset.filter(date__gte=utc_start)

    def filter_by_end_date(self, queryset, name, value):
        if not value:
            return queryset

        _, utc_end = self._local_day_range(value)
        return queryset.filter(date__lte=utc_end)

    @property
    def qs(self):
        queryset = super().qs
        return queryset.order_by("date")
