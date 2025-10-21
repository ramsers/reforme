from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand, DeleteClassCommand
from apps.classes.models import Classes
from apps.classes.utils.utils import _generate_recurring_classes
from django.utils import timezone
import copy
from django.db.models import Q


def handle_create_class(command: CreateClassCommand):
    new_class = Classes(
        title=command.title,
        description=command.description,
        size=command.size,
        date=command.date,
        instructor_id=command.instructor_id,
        recurrence_type=command.recurrence_type,
        recurrence_days=command.recurrence_days
    )

    new_class.save()

    if command.recurrence_type:
        _generate_recurring_classes(new_class)


    return new_class


def handle_partial_update_class(command: PartialUpdateClassCommand):
    class_to_update = Classes.objects.get(id=command.id)
    old_recurrence_type = class_to_update.recurrence_type
    old_recurrence_days = class_to_update.recurrence_days or []
    old_date = class_to_update.date
    root_class = class_to_update.parent_class or class_to_update
    fields_to_update = _collect_field_updates(command)

    # Apply updates
    for field, value in fields_to_update.items():
        setattr(class_to_update, field, value)
        if field in ['recurrence_type', 'recurrence_days']:
            setattr(root_class, field, value)

    class_to_update.save()
    root_class.save()

    # --- Case 1: only single class updated ---
    if not command.update_series:
        _emit_reschedule_event(class_to_update, update_series=False)
        return class_to_update

    # --- Case 2: update entire series ---
    recurrence_changed = _recurrence_changed(command, old_recurrence_type, old_recurrence_days)
    date_changed, time_changed = _detect_datetime_change(fields_to_update, old_date)

    if recurrence_changed:
        _regenerate_future_classes(root_class, class_to_update)
        _emit_reschedule_event(root_class, update_series=True)
        return class_to_update

    if time_changed and not date_changed:
        _shift_future_class_times(root_class, class_to_update, fields_to_update['date'])

    elif date_changed:
        _regenerate_future_classes(root_class, class_to_update)

    # Propagate non-date fields
    non_date_fields = {k: v for k, v in fields_to_update.items() if k not in ['date', 'recurrence_type', 'recurrence_days']}
    if non_date_fields:
        Classes.objects.filter(
            parent_class=root_class,
            date__gte=class_to_update.date
        ).update(**non_date_fields)

    _emit_reschedule_event(root_class, update_series=True)
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


def _collect_field_updates(command):
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


def _recurrence_changed(command, old_type, old_days):
    return (
        (command.recurrence_type is not None and old_type != command.recurrence_type)
        or (command.recurrence_days is not None and old_days != command.recurrence_days)
    )


def _detect_datetime_change(fields_to_update, old_date):
    if 'date' not in fields_to_update:
        return False, False
    new_date = fields_to_update['date']
    return new_date.date() != old_date.date(), new_date.time() != old_date.time()


def _regenerate_future_classes(root_class, class_to_update):
    from apps.classes.utils import _generate_recurring_classes
    from django.db.models import Q

    Classes.objects.filter(
        Q(parent_class=root_class) | Q(id=root_class.id),
        date__gt=class_to_update.date
    ).delete()
    _generate_recurring_classes(root_class)


def _shift_future_class_times(root_class, class_to_update, new_datetime):
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


def _emit_reschedule_event(cls, update_series: bool):
    from apps.classes.events import RescheduleClassEvent
    from apps.classes.event_dispatcher import event_dispatcher

    event = RescheduleClassEvent(
        class_id=str(cls.id),
        update_series=update_series,
        new_date=cls.date,
    )
    event_dispatcher.dispatch(event)

