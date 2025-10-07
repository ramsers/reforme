import typing as t
import os
import django_rq

class EventDispatcher:
    def __init__(self):
        self._handlers: list[tuple[type, t.Callable]] = []

    def add_handler(self, event_cls: type, handler: t.Callable):
        self._handlers.append((event_cls, handler))

    def dispatch(self, event, async_default: bool = True):
        """Dispatch an event instance. By default try async when possible."""
        # decide async: prefer environment flag or passed arg
        run_async = async_default and os.environ.get("APP_ENV") != "local"

        handlers = [h for (cls, h) in self._handlers if cls == event.__class__]
        if not handlers:
            return  # or raise

        for handler in handlers:
            if run_async:
                # uses default queue
                django_rq.enqueue(handler, event)
            else:
                handler(event)


# single global dispatcher instance
event_dispatcher = EventDispatcher()