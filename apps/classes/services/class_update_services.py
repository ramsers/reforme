from datetime import timedelta, date, datetime, time
from django.db.models import Q
import calendar
from django.utils import timezone

from apps.classes.models import Classes
from apps.classes.events.events import RescheduleClassEvent
from apps.classes.events.event_dispatchers import class_event_dispatcher
from dateutil.relativedelta import relativedelta
from apps.classes.value_objects import ClassRecurrenceType
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo


def apply_non_schedule_updates(root_class, cls, non_schedule_fields):
    if not non_schedule_fields:
        return

    for field, value in non_schedule_fields.items():
        setattr(cls, field, value)
        setattr(root_class, field, value)

        Classes.objects.filter(pk=cls.pk).update(**non_schedule_fields)

    if cls != root_class:
        Classes.objects.filter(pk=root_class.pk).update(**non_schedule_fields)

    propagate_non_date_fields(root_class, cls, non_schedule_fields)

def get_default_max_instances(rec_type: ClassRecurrenceType | None, rec_days: list[int]):
    if rec_type == "WEEKLY":
        return 52 * max(1, len(rec_days))
    return 10


def build_recurring_schedule(
    root_class: Classes,
    start_date: datetime,
    metadata_overrides: dict | None = None,
    max_instances: int | None = None,
):
    metadata_overrides = metadata_overrides or {}
    rec_type = root_class.recurrence_type
    rec_days = root_class.recurrence_days or []

    if max_instances is None:
        max_instances = get_default_max_instances(rec_type, rec_days)

    user_tz = start_date.tzinfo
    today_local = timezone.now().astimezone(user_tz).date()
    future_instances = []
    occurrences = 0


    def make_instance(local_dt: datetime):
        utc_dt = local_dt.astimezone(dt_timezone.utc)

        instance = Classes(
            title=root_class.title,
            description=root_class.description,
            size=root_class.size,
            date=utc_dt,
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

        current = start_date.date()

        while occurrences < max_instances:
            for offset in range(1, 8):
                day = current + timedelta(days=offset)

                if day <= today_local:
                    continue

                if day.weekday() not in rec_days:
                    continue

                local_dt = start_date.replace(year=day.year, month=day.month, day=day.day)

                future_instances.append(make_instance(local_dt))
                occurrences += 1

                if occurrences >= max_instances:
                    break

            current += timedelta(days=7)


    elif rec_type == "MONTHLY":

        current = start_date

        while occurrences < max_instances:
            current = current + relativedelta(months=1)
            year = current.year
            month = current.month
            target_day = start_date.day
            last_day = calendar.monthrange(year, month)[1]

            if target_day > last_day:
                continue

            local_dt = start_date.replace(year=year, month=month, day=target_day)

            if local_dt.date() <= today_local:
                continue

            future_instances.append(make_instance(local_dt))

            occurrences += 1

    elif rec_type == "YEARLY":
        for i in range(1, max_instances + 1):
            dt = start_date + relativedelta(years=i)
            if dt.date() > today_local:
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


def detect_datetime_change(fields_to_update, old_date, tzinfo=None):
    if 'date' not in fields_to_update:
        return False, False
    new_date = fields_to_update['date']

    if tzinfo:
        new_date = new_date.astimezone(tzinfo)
        old_date = old_date.astimezone(tzinfo)

    return new_date.date() != old_date.date(), new_date.timetz() != old_date.timetz()


def regenerate_future_classes(root_class: Classes, starting_from: Classes, metadata_overrides=None):
    metadata_overrides = metadata_overrides or {}
    user_tz = ZoneInfo(root_class.instructor.account.timezone)

    start_local = starting_from.date.astimezone(user_tz)
    delete_qs = Classes.objects.filter(parent_class=root_class)

    if starting_from.parent_class:
        delete_qs = delete_qs.filter(date__gte=starting_from.date)

    delete_qs.delete()

    new_instances = build_recurring_schedule(
        root_class=root_class,
        start_date=start_local,
        metadata_overrides=metadata_overrides,
        max_instances=None,
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

def handle_recurrence_update(root, cls, command, localized_existing, localized_incoming, non_schedule_fields):
    root.recurrence_type = command.recurrence_type
    root.recurrence_days = command.recurrence_days

    if command.recurrence_type == "WEEKLY" and command.recurrence_days:
        reference_local = localized_incoming or localized_existing
        aligned_local = align_datetime_to_recurrence(reference_local, command.recurrence_days)
        aligned_utc = aligned_local.astimezone(dt_timezone.utc)
        cls.date = aligned_utc
        if cls == root:
            root.date = aligned_utc

    root.save()
    if cls != root:
        cls.save(update_fields=["date"])

    apply_non_schedule_updates(root, cls, non_schedule_fields)
    emit_reschedule_event(root, update_series=True, recurrence_change=True)
    regenerate_future_classes(root, cls, metadata_overrides=non_schedule_fields)

    return cls


def handle_time_change(root, cls, new_time, non_schedule_fields):
    root.date = new_time if cls == root else root.date.replace(
        hour=new_time.hour,
        minute=new_time.minute,
        second=new_time.second,
        microsecond=new_time.microsecond,
    )

    cls.date = new_time

    if cls == root:
        root.save()
    else:
        root.save(update_fields=["date"])
        cls.save(update_fields=["date"])

    apply_non_schedule_updates(root, cls, non_schedule_fields)
    shift_future_class_times(root, cls, new_time)
    emit_reschedule_event(root, update_series=True)

    return cls


def handle_date_change(root, cls, new_date, non_schedule_fields):
    root.date = new_date if cls == root else root.date
    cls.date = new_date
    root.save(update_fields=["date"]) if cls != root else cls.save()

    apply_non_schedule_updates(root, cls, non_schedule_fields)
    regenerate_future_classes(root, cls, metadata_overrides=non_schedule_fields)
    emit_reschedule_event(root, update_series=True)

    return cls



def align_datetime_to_recurrence(start_dt: datetime, recurrence_days: list[int]):
    if not recurrence_days:
        return start_dt

    weekday = start_dt.weekday()

    if weekday in recurrence_days:
        return start_dt

    offset = min((day - weekday) % 7 or 7 for day in recurrence_days)
    return start_dt + timedelta(days=offset)