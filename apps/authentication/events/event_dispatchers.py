from apps.authentication.events.events import UserSignupEvent
from apps.core.dispatcher import EventDispatcher
from apps.authentication.events.event_handlers import handle_send_sign_up_email

auth_event_dispatcher = EventDispatcher()
auth_event_dispatcher.add_handler(UserSignupEvent, handle_send_sign_up_email)
