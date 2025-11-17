from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from apps.classes.models import Classes
from apps.classes.events.events import RescheduleClassEvent
from apps.classes.events.event_dispatchers import class_event_dispatcher
from dateutil.relativedelta import relativedelta


def generate_recurring_classes(base_class: Classes, count: int = 10):
    rec_type = base_class.recurrence_type
    rec_days = base_class.recurrence_days or []
    start_date = base_class.date
    now = timezone.now()

    existing_dates = set(
        Classes.objects.filter(
            instructor=base_class.instructor,
            title=base_class.title,
            recurrence_type=rec_type,
        ).values_list("date", flat=True)
    )

    future_instances = []

    for i in range(1, count + 1):
        if rec_type == "WEEKLY" and rec_days:
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
                        parent_class=base_class,
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
                    parent_class=base_class,
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
                    parent_class=base_class,
                )
            )

        else:
            continue

    if future_instances:
        Classes.objects.bulk_create(future_instances)



def collect_field_updates(command):
    fields = {}

    if command.title is not None:
        fields['title'] = command.title
    if command.description is not None:
        fields['description'] = command.description
    if command.size is not None:
        fields['size'] = command.size
    if command.date is not None:
        fields['date'] = command.date
    if command.recurrence_type is not None:
        fields['recurrence_type'] = command.recurrence_type
    if command.recurrence_days is not None:
        fields['recurrence_days'] = sorted(set(command.recurrence_days))
    return fields


def recurrence_changed(command, old_type, old_days):
    return (
        (command.recurrence_type is not None and old_type != command.recurrence_type)
        or (command.recurrence_days is not None and old_days != command.recurrence_days)
    )


def detect_datetime_change(fields_to_update, old_date):
    if 'date' not in fields_to_update:
        return False, False
    new_date = fields_to_update['date']
    return new_date.date() != old_date.date(), new_date.time() != old_date.time()


def regenerate_future_classes(root_class, class_to_update):
    Classes.objects.filter(
        Q(parent_class=root_class) | Q(id=root_class.id),
        date__gt=class_to_update.date
    ).delete()
    generate_recurring_classes(root_class)


def shift_future_class_times(root_class, class_to_update, new_datetime):
    future_classes = Classes.objects.filter(
        parent_class=root_class,
        date__gte=class_to_update.date
    )
    for c in future_classes:
        c.date = c.date.replace(
            hour=new_datetime.hour,
            minute=new_datetime.minute,
            second=new_datetime.second,
            microsecond=new_datetime.microsecond,
        )
    Classes.objects.bulk_update(future_classes, ['date'])


def emit_reschedule_event(cls, update_series: bool, recurrence_change=False):
    event = RescheduleClassEvent(
        class_id=str(cls.id),
        update_series=update_series,
        new_date=cls.date,
        recurrence_changed=recurrence_change,
    )
    class_event_dispatcher.dispatch(event)

