from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from apps.classes.models import Classes


@shared_task
def extend_future_classes():
    now = timezone.now()
    cutoff_date = now + timedelta(days=90)
    recurring_classes = Classes.objects.exclude(recurrence_type=None)
    to_create = []

    for base_class in recurring_classes:
        next_date = base_class.date

        while next_date <= cutoff_date:
            if base_class.recurrence_type == 'DAILY':
                next_date += timedelta(days=1)
            elif base_class.recurrence_type == 'WEEKLY':
                next_date += timedelta(weeks=1)
            elif base_class.recurrence_type == 'MONTHLY':
                next_date += relativedelta(months=1)
            elif base_class.recurrence_type == 'YEARLY':
                next_date += relativedelta(years=1)
            else:
                break

            if Classes.objects.filter(
                title=base_class.title,
                date=next_date,
                instructor=base_class.instructor
            ).exists():
                continue

            to_create.append(Classes(
                title=base_class.title,
                description=base_class.description,
                size=base_class.size,
                length=base_class.length,
                date=next_date,
                instructor=base_class.instructor,
                recurrence_type=base_class.recurrence_type,
                recurrence_days=base_class.recurrence_days,
            ))

    if to_create:
        Classes.objects.bulk_create(to_create)

    return f"Created {len(to_create)} new recurring classes"
