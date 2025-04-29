import json
from typing import Any, Dict, List

from confluent_kafka import Producer
from pydantic import BaseModel, Field

from .base import BaseSink


class KafkaSinkParams(BaseModel):
    bootstrap_servers: str = Field(
        ..., description="Kafka bootstrap servers", alias="bootstrap.servers"
    )
    topic: str = Field(..., description="Kafka topic to publish to", exclude=True)
    model_config = {"populate_by_name": True, "extra": "allow"}


class KafkaSink(BaseSink):
    def __init__(self, sink_params: Dict[str, Any]):
        self.params = KafkaSinkParams.model_validate(sink_params)
        self.topic = self.params.topic
        config = self.params.model_dump(by_alias=True)
        self.producer = Producer(config)

    def delivery_report(self, err, msg):
        """Reports message delivery status."""
        if err:
            print(f"❌ Message delivery failed: {err}")
        else:
            pass

    def publish(self, record: Dict[str, Any]) -> None:
        self.publish_bulk([record])

    def publish_bulk(self, records: List[Dict[str, Any]]) -> None:
        for msg in records:
            message_value = json.dumps(msg) if isinstance(msg, dict) else msg
            self.producer.produce(
                self.topic,
                value=message_value.encode("utf-8"),
                callback=self.delivery_report,
            )
            self.producer.poll(0)  # Trigger message delivery
        self.producer.flush()  # Ensure all messages are sent

    def close(self) -> None:
        self.producer.flush()
