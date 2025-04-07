import csv
from pathlib import Path
from typing import Any, Dict, List
from glassgen.sinks.base import BaseSink

class CSVSink(BaseSink):
    def __init__(self, sink_params: dict):
        filepath = sink_params["path"]
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

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        if self.writer is None:
            self.file = open(self.filepath, 'w', newline='')
            self.fieldnames = list(data[0].keys())
            self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
            self.writer.writeheader()
            
        self.writer.writerows(data)

    def close(self) -> None:
        if self.file:
            self.file.close()
