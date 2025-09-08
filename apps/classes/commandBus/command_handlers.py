from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand
from apps.classes.models import Classes


def handle_create_class(command: CreateClassCommand):
    new_class = Classes(
        name=command.name,
        size=command.size,
        date=command.date,
        instructor_id=command.instructor_id
    )

    new_class.save()
    return new_class


def handle_partial_update_class(command: PartialUpdateClassCommand):
    class_to_update = Classes.objects.get(id=command.id)

    if command.name is not None:
        class_to_update.name = command.name
    if command.size is not None:
        class_to_update.size = command.size
    if command.date is not None:
        class_to_update.date = command.date

    class_to_update.save()
    return class_to_update
