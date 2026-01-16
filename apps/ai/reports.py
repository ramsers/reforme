from datetime import timedelta
from django.utils import timezone
from django.db.models import Max, Q

from apps.user.models import User
from apps.user.value_objects import Role


def get_inactive_clients(window_days: int = 30, limit: int = 200):
    cutoff = timezone.now() - timedelta(days=window_days)

    qs = (
        User.objects
        .filter(role=Role.CLIENT)
        .annotate(last_booking_at=Max("booked_class__created_at"))
        .filter(Q(last_booking_at__lt=cutoff) | Q(last_booking_at__isnull=True))
        .order_by("last_booking_at")
    )

    now = timezone.now()
    rows = []

    for u in qs[:limit]:
        last = u.last_booking_at
        days_inactive = (now - last).days if last else None

        rows.append({
            "client_id": str(u.id),
            "name": u.name,
            "email": u.email,
            "last_booking_at": last.isoformat() if last else None,
            "days_inactive": days_inactive if days_inactive is not None else f">{window_days}",
        })

    return rows
