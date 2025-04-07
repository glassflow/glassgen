import json
from pathlib import Path
from typing import Any, Dict, List
from glassgen.sinks.base import BaseSink

class JSONSink(BaseSink):
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data: List[Dict[str, Any]] = []

    def publish(self, data: Dict[str, Any]) -> None:
        self.data.append(data)
    
    def close(self) -> None:
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        self.data.extend(data)
