from apps.authentication.events.event_dispatchers import authentication_event_dispatcher
from apps.user.commandBus.commands import CreateUserCommand, UpdateUserCommand
from apps.user.models import User
from apps.authentication.events.events import UserSignupEvent


def handle_create_user(command: CreateUserCommand):
    user = User(
        name=command.name,
        email=command.email,
        phone_number=command.phone_number,
        role=command.role
    )

    if command.password:
        user.set_password(command.password)

    user.save()

    event = UserSignupEvent(user_id=user.id)
    authentication_event_dispatcher.dispatch(event)

    return user


def handle_update_user(command: UpdateUserCommand):
    user = User.objects.get(id=command.id)

    if command.name:
        user.name = command.name
    if command.email:
        user.email = command.email
    if command.phone_number:
        user.phone_number = command.phone_number
    if command.password:
        user.set_password(command.password)
    if command.role:
        user.role = Role(command.role)

    user.save()
    return user
