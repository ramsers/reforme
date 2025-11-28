import typing as t
import os
import django_rq

class EventDispatcher:
    def __init__(self):
        self._handlers: list[tuple[type, t.Callable]] = []

    def add_handler(self, event_cls: type, handler: t.Callable):
        self._handlers.append((event_cls, handler))

    def dispatch(self, event, async_default: bool = True):
        env = os.environ.get("APP_ENV", "local").lower()
        run_async = async_default and env not in ("local", "test")
        handlers = [h for (cls, h) in self._handlers if cls == event.__class__]
        if not handlers:
            return

        for handler in handlers:
            if run_async:
                django_rq.enqueue(handler, event)
            else:
                handler(event)

event_dispatcher = EventDispatcher()
