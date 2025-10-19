from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand
from apps.classes.models import Classes
from apps.classes.utils.utils import _generate_recurring_classes
from django.utils import timezone
import copy



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
    fields_to_update = {}

    # --- Detect and store changes ---
    if command.title is not None:
        fields_to_update['title'] = command.title
    if command.description is not None:
        fields_to_update['description'] = command.description
    if command.size is not None:
        fields_to_update['size'] = command.size
    if command.date is not None:
        fields_to_update['date'] = command.date
    if command.recurrence_type is not None:
        fields_to_update['recurrence_type'] = command.recurrence_type
    if command.recurrence_days is not None:
        new_days = sorted(set(command.recurrence_days))
        root_class.recurrence_days = new_days
        class_to_update.recurrence_days = new_days
        fields_to_update['recurrence_days'] = new_days
        fields_to_update['recurrence_days'] = new_days
    # --- Apply updates to both base and root classes ---
    for field, value in fields_to_update.items():
        setattr(class_to_update, field, value)
        if field in ['recurrence_type', 'recurrence_days']:
            setattr(root_class, field, value)

    class_to_update.save()
    root_class.save()

    # --- If not updating series, stop here ---
    if not command.update_series:
        return class_to_update

    # --- Determine what changed ---
    recurrence_changed = (
        command.recurrence_type is not None
        and old_recurrence_type != command.recurrence_type
    ) or (
        command.recurrence_days is not None
        and old_recurrence_days != command.recurrence_days
    )

    date_changed = False
    time_changed = False
    if 'date' in fields_to_update:
        new_datetime = fields_to_update['date']
        date_changed = new_datetime.date() != old_date.date()
        time_changed = new_datetime.time() != old_date.time()

    # --- Handle recurrence structure changes first ---
    if recurrence_changed:
        Classes.objects.filter(
            parent_class=root_class,
            date__gt=class_to_update.date
        ).delete()
        _generate_recurring_classes(root_class)
        return class_to_update

    # --- Handle date/time changes ---
    if time_changed and not date_changed:
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

    elif date_changed:
        Classes.objects.filter(
            parent_class=root_class,
            date__gt=class_to_update.date
        ).delete()
        _generate_recurring_classes(root_class)

    # --- Propagate non-date changes (title, size, description) ---
    non_date_fields = {k: v for k, v in fields_to_update.items() if k not in ['date', 'recurrence_type', 'recurrence_days']}
    if non_date_fields:
        Classes.objects.filter(
            parent_class=root_class,
            date__gte=class_to_update.date
        ).update(**non_date_fields)

    return class_to_update

