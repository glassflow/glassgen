import json
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from glassgen.sinks.base import BaseSink


class NDJSONSinkParams(BaseModel):
    path: str = Field(..., description="Path to the output NDJSON file")


class NDJSONSink(BaseSink):
    def __init__(self, sink_params: Dict[str, Any]):
        params = NDJSONSinkParams.model_validate(sink_params)
        self.filepath = Path(params.path)
        self.file = None

    def _open(self) -> None:
        if self.file is None:
            self.file = open(self.filepath, "w")

    def publish(self, data: Dict[str, Any]) -> None:
        self._open()
        self.file.write(json.dumps(data) + "\n")

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        self._open()
        for record in data:
            self.file.write(json.dumps(record) + "\n")

    def close(self) -> None:
        if self.file:
            self.file.close()
