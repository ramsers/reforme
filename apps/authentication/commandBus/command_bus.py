from pymessagebus._commandbus import CommandBus


auth_command_bus = CommandBus(locking=True)
auth_command_bus.add_handler(RequestResetPasswordCommand, handle_request_password_reset)

