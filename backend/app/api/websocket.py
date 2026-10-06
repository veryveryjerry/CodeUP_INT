import asyncio
import json
from typing import Dict, List, Any
from ..models import AgentEvent

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}

    async def publish(self, topic: str, event: AgentEvent):
        if topic in self.subscribers:
            event_json = event.model_dump_json()
            for queue in self.subscribers[topic]:
                await queue.put(event_json)

    def subscribe(self, topic: str) -> asyncio.Queue:
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        queue = asyncio.Queue()
        self.subscribers[topic].append(queue)
        return queue

    def unsubscribe(self, topic: str, queue: asyncio.Queue):
        if topic in self.subscribers:
            self.subscribers[topic].remove(queue)
            if not self.subscribers[topic]:
                del self.subscribers[topic]

event_bus = EventBus()
