from pymessagebus._commandbus import CommandBus


from apps.user.commandBus.commands import CreateUserCommand, UpdateUserCommand, DeleteUserCommand
from apps.user.commandBus.command_handlers import handle_create_user, handle_update_user, handle_delete_user

user_command_bus = CommandBus(locking=False)
user_command_bus.add_handler(CreateUserCommand, handle_create_user)
user_command_bus.add_handler(UpdateUserCommand, handle_update_user)
user_command_bus.add_handler(DeleteUserCommand, handle_delete_user)

