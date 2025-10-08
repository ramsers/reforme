from pymessagebus._commandbus import CommandBus

from apps.payment.commandBus.commands import CreatePassPurchaseCommand
from apps.payment.commandBus.command_handlers import handle_create_pass_purchase

payment_command_bus = CommandBus(locking=False)
payment_command_bus.add_handler(CreatePassPurchaseCommand, handle_create_pass_purchase)
