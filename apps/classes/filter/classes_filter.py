import django_filters
from apps.classes.models import Classes


class ClassesFilter(django_filters.FilterSet):
    # Filter classes happening on an exact day
    date = django_filters.DateFilter(field_name="date", lookup_expr="date")

    # Range filtering
    start_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Classes
        fields = ["date", "start_date", "end_date", "instructor"]
