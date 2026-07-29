from typing import Dict, Any, List, Optional
import logging
from src.domain.interfaces.connector import IConnector

logger = logging.getLogger("document_intelligence.connector_registry")


class ConnectorRegistry:
    """Centralized Registry for Enterprise System Connectors."""

    _connectors: Dict[str, IConnector] = {}

    @classmethod
    def register_connector(cls, connector_id: str, connector: IConnector):
        cls._connectors[connector_id] = connector
        info = connector.connector_info()
        logger.info(f"Registered Enterprise Connector: '{connector_id}' ({info.get('name')})")

    @classmethod
    def get_connector(cls, connector_id: str) -> Optional[IConnector]:
        return cls._connectors.get(connector_id)

    @classmethod
    def list_connectors(cls) -> List[Dict[str, Any]]:
        return [{"connector_id": cid, **c.connector_info()} for cid, c in cls._connectors.items()]
