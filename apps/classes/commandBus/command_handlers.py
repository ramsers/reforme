from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand, DeleteClassCommand
from apps.classes.models import Classes
from django.utils import timezone
import copy
from django.db.models import Q
import datetime
from datetime import timedelta
from apps.classes.services.class_update_services import (build_recurring_schedule,
                                                         recurrence_changed, regenerate_future_classes,
                                                         detect_datetime_change, emit_reschedule_event,
                                                         collect_field_updates, shift_future_class_times,
                                                         propagate_non_date_fields)
from apps.classes.events.events import DeletedClassEvent
from apps.classes.events.event_dispatchers import class_event_dispatcher


def handle_create_class(command: CreateClassCommand):
    start_date = command.date
    recurrence_type = command.recurrence_type
    recurrence_days = command.recurrence_days or []

    if recurrence_type == "WEEKLY" and recurrence_days:
        weekday = start_date.weekday()
        if weekday not in recurrence_days:
            days_until_next = min((d - weekday) % 7 for d in recurrence_days)
            start_date += timedelta(days=days_until_next)

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
            start_date=start_date,
            metadata_overrides=None,
            max_instances=10,
        )
        Classes.objects.bulk_create(future_instances)

    return new_class


def handle_partial_update_class(command: PartialUpdateClassCommand):
    cls = Classes.objects.get(id=command.id)

    old_date = cls.date
    old_rec_type = cls.recurrence_type
    old_rec_days = cls.recurrence_days or []
    fields = collect_field_updates(command)

    date_changed, time_changed = detect_datetime_change(fields, old_date)
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

    root = cls.parent_class or cls

    if rec_changed:
        root.recurrence_type = command.recurrence_type
        root.recurrence_days = command.recurrence_days
        root.save()
        regenerate_future_classes(root, cls, metadata_overrides=non_schedule_fields)
        emit_reschedule_event(root, update_series=True, recurrence_change=True)
        return cls

    if time_changed and not date_changed:
        cls.date = fields["date"]
        cls.save()

        shift_future_class_times(root, cls, fields["date"])
        emit_reschedule_event(root, update_series=True)
        return cls

    if date_changed:
        regenerate_future_classes(root, cls, metadata_overrides=non_schedule_fields)
        emit_reschedule_event(root, update_series=True)
        return cls

    if non_schedule_fields:
        propagate_non_date_fields(root, cls, non_schedule_fields)

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
