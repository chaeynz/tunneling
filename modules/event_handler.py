# pylint: disable=missing-docstring
from enum import Enum, auto
from typing import Callable


class Event(Enum):
    MESSAGE_RECV = auto()


class EventHandler:
    def __init__(self):
        self._events: dict = {}

    def subscribe(self, event:Event, callback: Callable):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)

    def notify(self, event:Event, *args, **kwargs):
        if event in self._events:
            for callback in self._events[event]:
                callback(*args, **kwargs)

if __name__ == "__main__":
    handler = EventHandler()
    handler.subscribe(Event.MESSAGE_RECV, lambda msg: print(f"I was called! Message: {msg}"))
    handler.notify(Event.MESSAGE_RECV, msg="Hello from main!")
