import src.simulation.event.Event as Event

class EventQueue:

    def __init__(self):
        self.events = []

    def push(self, event: Event):
        self.events.append(event)
        self.events.sort(key=lambda x: x.time, reverse=True)

    def pop(self) -> Event:
        return self.events.pop() if not self.is_empty() else None

    def is_empty(self):
        return len(self.events) == 0
