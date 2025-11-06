from pymessagebus._commandbus import CommandBus

from apps.payment.commandBus.commands import (CreatePurchaseIntentCommand, CreatePassPurchaseCommand,
                                              CancelSubscriptionWebhookCommand, CancelSubscriptionCommand)
from apps.payment.commandBus.command_handlers import (handle_create_purchase_intent, handle_create_pass_purchase,
                                                      handle_update_subscription_cancellation, handle_cancel_subscription)

payment_command_bus = CommandBus(locking=False)
payment_command_bus.add_handler(CreatePurchaseIntentCommand, handle_create_purchase_intent)
payment_command_bus.add_handler(CreatePassPurchaseCommand, handle_create_pass_purchase)
payment_command_bus.add_handler(CancelSubscriptionCommand, handle_cancel_subscription)
payment_command_bus.add_handler(CancelSubscriptionWebhookCommand, handle_update_subscription_cancellation)
