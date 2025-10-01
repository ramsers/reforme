import django_filters
from django.db.models import Q
from apps.user.models import User

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = User
        fields = []

    def filter_search(self, queryset, name, value):
        """
        Filters users where first name, last name, or email contains the search value (case-insensitive)
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(email__icontains=value)
        )
