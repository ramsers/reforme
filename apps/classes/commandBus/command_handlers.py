from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand
from apps.classes.models import Classes
from apps.classes.utils.utils import _generate_recurring_classes
from django.utils import timezone



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
    old_recurrence_days = class_to_update.recurrence_days
    root_class = class_to_update.parent_class or class_to_update

    print('old_recurrence_type ======================', old_recurrence_type, flush=True)
    print('old_recurrence_days ======================', old_recurrence_days, flush=True)
    print('recurrence_type ======================', command.recurrence_type, flush=True)

    if command.title is not None:
        class_to_update.title = command.title
    if command.description is not None:
        class_to_update.description = command.description
    if command.size is not None:
        class_to_update.size = command.size
    if command.date is not None:
        class_to_update.date = command.date
    if command.recurrence_type is not None:
        root_class.recurrence_type = command.recurrence_type
        class_to_update.recurrence_type = command.recurrence_type
    if command.recurrence_days is not None:
        root_class.recurrence_days = command.recurrence_days
        class_to_update.recurrence_days = command.recurrence_days

    class_to_update.save()
    root_class.save()

    if root_class.recurrence_type:
        # Delete all future classes in this series after the edited class
        Classes.objects.filter(
            parent_class=root_class,
            date__gt=class_to_update.date
        ).delete()

        # Regenerate future classes from the updated class as the new pattern seed
        _generate_recurring_classes(root_class)

    # if old_recurrence_type != command.recurrence_type or old_recurrence_days != command.recurrence_days:
    #     Classes.objects.filter(
    #         parent_class=root_class,
    #         date__gt=timezone.now()
    #     ).delete()
    #
    # if (
    #     (old_recurrence_type != command.recurrence_type or old_recurrence_days != command.recurrence_days)
    # ):
    #     print('I AM HITTING THE IF ==================', flush=True)
    #     if old_recurrence_type:
    #         Classes.objects.filter(
    #             instructor=class_to_update.instructor,
    #             title=class_to_update.title,
    #             recurrence_type=old_recurrence_type,
    #             date__gt=timezone.now(),
    #         ).exclude(id=class_to_update.id).delete()
    #
    #     if command.recurrence_type:
    #         _generate_recurring_classes(class_to_update)

    return class_to_update
