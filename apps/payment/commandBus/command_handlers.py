from apps.payment.commandBus.commands import CreatePassPurchaseCommand

def handle_create_pass_purchase(command: CreatePassPurchaseCommand):
    print('Im hitting purchase command ===========')