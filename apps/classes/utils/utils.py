from datetime import timedelta
from dateutil.relativedelta import relativedelta
import datetime
from apps.classes.models import Classes
from django.utils import timezone


def _generate_recurring_classes(base_class: Classes, count: int = 10):
    """
    Generate a series of future class instances based on recurrence settings.
    Does not duplicate the base instance.
    """

    # if not base_class.recurrence_type:
    #     return

    print('HITTING GENERATE CLASSES =================', base_class, flush=True)
    rec_type = base_class.recurrence_type
    rec_days = base_class.recurrence_days or []
    start_date = base_class.date
    now = timezone.now()

    print('HITTING GENERATE rec_type =================', rec_type, flush=True)
    print('HITTING GENERATE rec_days =================', rec_days, flush=True)
    print('HITTING GENERATE start_date =================', start_date, flush=True)

    existing_dates = set(
        Classes.objects.filter(
            instructor=base_class.instructor,
            title=base_class.title,
            recurrence_type=rec_type,
        ).values_list("date", flat=True)
    )

    future_instances = []

    for i in range(1, count + 1):
        if rec_type == "DAILY":

            next_date = start_date + timedelta(days=i)

            # if next_date in existing_dates or next_date <= now:
            #     continue

            future_instances.append(
                Classes(
                    title=base_class.title,
                    description=base_class.description,
                    size=base_class.size,
                    date=next_date,
                    instructor=base_class.instructor,
                    recurrence_type=None,
                    recurrence_days=None,
                    parent_class=base_class,  # ✅ link to root
                )
            )
            continue
            print('HITTING  DAILY next_date =================', next_date, flush=True)


        elif rec_type == "WEEKLY" and rec_days:
            for day in rec_days:
                day_offset = (day - start_date.weekday()) % 7 + 7 * (i - 1)
                next_date = start_date + timedelta(days=day_offset)

                if next_date in existing_dates or next_date <= now:
                    continue

                future_instances.append(
                    Classes(
                        title=base_class.title,
                        description=base_class.description,
                        size=base_class.size,
                        date=next_date,
                        instructor=base_class.instructor,
                        recurrence_type=None,
                        recurrence_days=None,
                        parent_class=base_class,  # ✅ link to root
                    )
                )
            continue

        elif rec_type == "MONTHLY":
            next_date = start_date + relativedelta(months=i)

            if next_date in existing_dates or next_date <= now:
                continue

            future_instances.append(
                Classes(
                    title=base_class.title,
                    description=base_class.description,
                    size=base_class.size,
                    date=next_date,
                    instructor=base_class.instructor,
                    parent_class=base_class,  # ✅ link to root
                )
            )

        elif rec_type == "YEARLY":
            next_date = start_date + relativedelta(years=i)

            if next_date in existing_dates or next_date <= now:
                continue

            future_instances.append(
                Classes(
                    title=base_class.title,
                    description=base_class.description,
                    size=base_class.size,
                    date=next_date,
                    instructor=base_class.instructor,
                    parent_class=base_class,  # ✅ link to root
                )
            )

        else:
            continue

    if future_instances:
        Classes.objects.bulk_create(future_instances)
