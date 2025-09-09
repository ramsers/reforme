from pymessagebus._commandbus import CommandBus
from apps.booking.commandBus.commands import CreateBookingCommand
from apps.booking.commandBus.command_handlers import handle_create_booking

booking_command_bus = CommandBus(locking=True)
booking_command_bus.add_handler(CreateBookingCommand, handle_create_booking)
