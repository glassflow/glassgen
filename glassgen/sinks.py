import csv
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import uuid
from kafka import KafkaProducer
from pathlib import Path

class BaseSink(ABC):
    @abstractmethod
    def publish(self, data: Dict[str, Any]) -> None:
        """Publish a single record to the sink"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the sink and release resources"""
        pass

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

class JSONSink(BaseSink):
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data: List[Dict[str, Any]] = []

    def publish(self, data: Dict[str, Any]) -> None:
        self.data.append(data)

    def close(self) -> None:
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

class KafkaSink(BaseSink):
    def __init__(self, bootstrap_servers: str, topic: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic

    def publish(self, data: Dict[str, Any]) -> None:
        self.producer.send(self.topic, value=data)

    def close(self) -> None:
        self.producer.close() 