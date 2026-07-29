import asyncio
import logging
from typing import List, Callable, Dict, Type
from src.domain.events.document_events import DomainEvent
from src.domain.interfaces.event_publisher import IDomainEventPublisher

logger = logging.getLogger("document_intelligence.events")


class InMemoryEventBus(IDomainEventPublisher):
    """Asynchronous in-memory event publisher implementation."""

    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        logger.info(f"Publishing domain event [{event.__class__.__name__}]: {event.event_id}")
        handlers = self._subscribers.get(type(event), [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error handling event {event.event_id} in {handler}: {e}")
