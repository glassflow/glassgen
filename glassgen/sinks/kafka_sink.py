import json
from typing import Any, Dict
from kafka import KafkaProducer
from glassgen.sinks.base import BaseSink

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