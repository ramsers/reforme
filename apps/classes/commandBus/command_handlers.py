from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand, DeleteClassCommand
from apps.classes.models import Classes
from django.utils import timezone
import copy
from django.db.models import Q
import datetime
from datetime import timedelta
from apps.classes.services.class_update_services import (generate_recurring_classes, recurrence_changed,
                                                         regenerate_future_classes, detect_datetime_change,
                                                         emit_reschedule_event, collect_field_updates, shift_future_class_times)


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
        generate_recurring_classes(new_class)

    return new_class


def handle_partial_update_class(command: PartialUpdateClassCommand):
    class_to_update = Classes.objects.get(id=command.id)
    old_recurrence_type = class_to_update.recurrence_type
    old_recurrence_days = class_to_update.recurrence_days or []
    old_date = class_to_update.date
    root_class = class_to_update.parent_class or class_to_update
    fields_to_update = collect_field_updates(command)

    for field, value in fields_to_update.items():
        setattr(class_to_update, field, value)
        if field in ['recurrence_type', 'recurrence_days']:
            setattr(root_class, field, value)

    class_to_update.save()
    root_class.save()

    if not command.update_series:
        emit_reschedule_event(class_to_update, update_series=False)
        return class_to_update

    recurrence_change = recurrence_changed(command, old_recurrence_type, old_recurrence_days)
    date_changed, time_changed = detect_datetime_change(fields_to_update, old_date)

    if recurrence_changed:
        emit_reschedule_event(root_class, update_series=True, recurrence_change=recurrence_change)
        regenerate_future_classes(root_class, class_to_update)
        return class_to_update

    if time_changed and not date_changed:
        shift_future_class_times(root_class, class_to_update, fields_to_update['date'])

    elif date_changed:
        regenerate_future_classes(root_class, class_to_update)

    non_date_fields = {k: v for k, v in fields_to_update.items() if k not in ['date', 'recurrence_type', 'recurrence_days']}
    if non_date_fields:
        Classes.objects.filter(
            parent_class=root_class,
            date__gte=class_to_update.date
        ).update(**non_date_fields)

    emit_reschedule_event(root_class, update_series=True)
    return class_to_update


def handle_delete_class(command: DeleteClassCommand):
    class_to_delete = Classes.objects.get(id=command.id)
    root_class = class_to_delete.parent_class or class_to_delete

    if command.delete_series:
        Classes.objects.filter(
                Q(parent_class=root_class) | Q(id=root_class.id),
                date__gte=class_to_delete.date
            ).delete()
    else:
        class_to_delete.delete()
