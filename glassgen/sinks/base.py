from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseSink(ABC):
    @abstractmethod
    def publish(self, data: Dict[str, Any]) -> None:
        """Publish a single record to the sink"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the sink and release resources"""
        pass

    @abstractmethod
    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        """Publish a bulk of records to the sink"""
        pass
