from datetime import timedelta, date, datetime, time
from django.db.models import Q
from django.utils import timezone

from apps.classes.models import Classes
from apps.classes.events.events import RescheduleClassEvent
from apps.classes.events.event_dispatchers import class_event_dispatcher
from dateutil.relativedelta import relativedelta


def build_recurring_schedule(
    root_class: Classes,
    start_date: date,
    metadata_overrides: dict | None = None,
    max_instances: int = 10,
):
    metadata_overrides = metadata_overrides or {}
    rec_type = root_class.recurrence_type
    rec_days = root_class.recurrence_days or []
    today = timezone.now().date()
    future_instances = []
    occurrences = 0

    if isinstance(start_date, datetime):
        start_date = start_date.date()

    def make_instance(for_date):
        parent_dt = root_class.date

        child_dt = parent_dt.replace(
            year=for_date.year,
            month=for_date.month,
            day=for_date.day,
        )

        instance = Classes(
            title=root_class.title,
            description=root_class.description,
            size=root_class.size,
            date=child_dt,
            instructor=root_class.instructor,
            parent_class=root_class,
            recurrence_type=None,
            recurrence_days=None,
        )
        for field, value in metadata_overrides.items():
            setattr(instance, field, value)
        return instance

    if rec_type == "WEEKLY":
        if not rec_days:
            return []

        current = start_date

        while occurrences < max_instances:
            for offset in range(1, 8):
                dt = current + timedelta(days=offset)

                if dt <= today:
                    continue

                if dt.weekday() not in rec_days:
                    continue

                future_instances.append(make_instance(dt))
                occurrences += 1

                if occurrences >= max_instances:
                    break

            current += timedelta(days=7)

    elif rec_type == "MONTHLY":
        for i in range(1, max_instances + 1):
            dt = start_date + relativedelta(months=i)
            if dt > today:
                future_instances.append(make_instance(dt))

    elif rec_type == "YEARLY":
        for i in range(1, max_instances + 1):
            dt = start_date + relativedelta(years=i)
            if dt > today:
                future_instances.append(make_instance(dt))

    return future_instances


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
    if command.instructor_id is not None:
        fields['instructor_id'] = command.instructor_id
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


def regenerate_future_classes(root_class: Classes, starting_from: Classes,  metadata_overrides=None):
    metadata_overrides = metadata_overrides or {}

    Classes.objects.filter(
        parent_class=root_class,
        date__gte=starting_from.date,
    ).delete()

    new_instances = build_recurring_schedule(
        root_class=root_class,
        start_date=starting_from.date.date(),
        metadata_overrides=metadata_overrides,
        max_instances=10,
    )

    if new_instances:
        Classes.objects.bulk_create(new_instances)


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


def propagate_non_date_fields(root_class, class_to_update, non_date_fields):
    if not non_date_fields:
        return
    Classes.objects.filter(
        parent_class=root_class,
        date__gte=class_to_update.date
    ).update(**non_date_fields)
