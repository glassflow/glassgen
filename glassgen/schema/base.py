from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSchema(ABC):
    """Base class for all schemas"""
    
    @abstractmethod
    def validate(self) -> None:
        """Validate the schema configuration"""
        pass
    
    @abstractmethod
    def _generate_record(self) -> Dict[str, Any]:
        """Generate a single record based on the schema"""
        pass
