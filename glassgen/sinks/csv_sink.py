import csv
from pathlib import Path
from typing import Any, Dict
from glassgen.sinks.base import BaseSink

class CSVSink(BaseSink):
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.writer = None
        self.file = None
        self.fieldnames = None

    def publish(self, data: Dict[str, Any]) -> None:
        if self.writer is None:
            self.file = open(self.filepath, 'w', newline='')
            self.fieldnames = list(data.keys())
            self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
            self.writer.writeheader()
        
        self.writer.writerow(data)

    def close(self) -> None:
        if self.file:
            self.file.close()
