from abc import ABC, abstractmethod
from src.domain.events.document_events import DomainEvent


class IDomainEventPublisher(ABC):
    """Abstract publisher interface for decoupled domain event dispatching."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass
