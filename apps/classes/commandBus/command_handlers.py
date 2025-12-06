from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand, DeleteClassCommand
from apps.classes.models import Classes
from django.utils import timezone
import copy
from django.db.models import Q
import datetime
from datetime import timedelta

from apps.classes.selectors.selectors import get_class_by_id
from apps.classes.services.class_update_services import (build_recurring_schedule,
                                                         recurrence_changed, detect_datetime_change,
                                                         emit_reschedule_event, collect_field_updates,
                                                         align_datetime_to_recurrence, apply_non_schedule_updates,
                                                         handle_recurrence_update, handle_time_change,
                                                         handle_date_change)
from apps.classes.events.events import DeletedClassEvent
from apps.classes.events.event_dispatchers import class_event_dispatcher
from zoneinfo import ZoneInfo
from datetime import timezone as dt_timezone


def handle_create_class(command: CreateClassCommand):
    start_date = command.date
    recurrence_type = command.recurrence_type
    recurrence_days = command.recurrence_days or []
    user_tz = ZoneInfo(command.user_timezone)
    localized_start = start_date.astimezone(user_tz)

    if recurrence_type == "WEEKLY" and recurrence_days:
        localized_start = align_datetime_to_recurrence(localized_start, recurrence_days)

    start_date = localized_start.astimezone(dt_timezone.utc)

    new_class = Classes.objects.create(
        title=command.title,
        description=command.description,
        size=command.size,
        date=start_date,
        instructor_id=command.instructor_id,
        recurrence_type=recurrence_type,
        recurrence_days=recurrence_days,
    )

    if recurrence_type:
        future_instances = build_recurring_schedule(
            root_class=new_class,
            start_date=localized_start,
            metadata_overrides=None,
            max_instances=None,
        )
        Classes.objects.bulk_create(future_instances)

    return new_class


def handle_partial_update_class(command: PartialUpdateClassCommand):
    cls = get_class_by_id(command.id)
    root = cls.parent_class or cls
    user_tz = ZoneInfo(root.instructor.account.timezone)

    old_date = cls.date
    old_rec_type = root.recurrence_type if command.update_series else cls.recurrence_type
    old_rec_days = (root.recurrence_days or []) if command.update_series else (cls.recurrence_days or [])
    fields = collect_field_updates(command)
    localized_existing = cls.date.astimezone(user_tz)
    localized_incoming = fields.get("date").astimezone(user_tz) if "date" in fields else None

    if command.update_series and cls.parent_class and "date" in fields:
        aligned_local = localized_existing.replace(
            hour=localized_incoming.hour,
            minute=localized_incoming.minute,
            second=localized_incoming.second,
            microsecond=localized_incoming.microsecond,
        )

        localized_incoming = aligned_local

    if localized_incoming:
        fields["date"] = localized_incoming.astimezone(dt_timezone.utc)

    change_fields = {"date": localized_incoming} if localized_incoming else {}
    date_changed, time_changed = detect_datetime_change(
        change_fields or fields,
        localized_existing if change_fields else old_date,
        tzinfo=None if change_fields else user_tz,
    )
    rec_changed = recurrence_changed(command, old_rec_type, old_rec_days)

    non_schedule_fields = {
        name: value
        for name, value in fields.items()
        if name not in ["date", "recurrence_type", "recurrence_days"]
    }

    if not command.update_series:
        for field, value in fields.items():
            setattr(cls, field, value)

        cls.save()

        if date_changed or time_changed:
            emit_reschedule_event(cls, update_series=False)

        return cls


    if rec_changed:
        handle_recurrence_update(root, cls, command, localized_existing, localized_incoming, non_schedule_fields)

    if time_changed and not date_changed:
        return handle_time_change(root, cls, fields["date"], non_schedule_fields)

    if date_changed:
        return handle_date_change(root, cls, fields["date"], non_schedule_fields)

    if non_schedule_fields:
        apply_non_schedule_updates(root, cls, non_schedule_fields)

    return cls


def handle_delete_class(command: DeleteClassCommand):
    class_to_delete = Classes.objects.get(id=command.id)
    root_class = class_to_delete.parent_class or class_to_delete

    event = DeletedClassEvent(
        class_id=class_to_delete.id,
    )

    class_event_dispatcher.dispatch(event)

    if command.delete_series:
        Classes.objects.filter(
                Q(parent_class=root_class) | Q(id=root_class.id),
                date__gte=class_to_delete.date
            ).delete()
    else:
        class_to_delete.delete()
