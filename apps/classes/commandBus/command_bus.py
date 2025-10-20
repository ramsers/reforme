from pymessagebus._commandbus import CommandBus
from apps.classes.commandBus.commands import CreateClassCommand, PartialUpdateClassCommand, DeleteClassCommand
from apps.classes.commandBus.command_handlers import (handle_create_class, handle_partial_update_class,
                                                      handle_delete_class)

classes_command_bus = CommandBus(locking=False)
classes_command_bus.add_handler(CreateClassCommand, handle_create_class)
classes_command_bus.add_handler(PartialUpdateClassCommand, handle_partial_update_class)
classes_command_bus.add_handler(DeleteClassCommand, handle_delete_class)

