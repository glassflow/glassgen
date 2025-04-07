from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseSink(ABC):
    @abstractmethod
    def publish(self, data: Dict[str, Any]) -> None:
        """Publish a single record to the sink"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the sink and release resources"""
        pass