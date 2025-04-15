from typing import Any, Dict, List
from pydantic import BaseModel, Field
from glassgen.sinks.base import BaseSink
from glassgen.sinks.kafka import BaseKafkaClient
import socket


class ConfluentKafkaSinkParams(BaseModel):
    bootstrap_servers: str = Field(..., description="Kafka bootstrap servers")
    topic: str = Field(..., description="Kafka topic to publish to")
    security_protocol: str = Field(default="SASL_SSL", description="Security protocol for Kafka connection")
    sasl_mechanism: str = Field(default="PLAIN", description="SASL mechanism for authentication")
    username: str = Field(..., description="SASL username for authentication")
    password: str = Field(..., description="SASL password for authentication")
    client_id: str = Field(default_factory=socket.gethostname, description="Client ID for Kafka connection")
    
    @property
    def client_config(self) -> Dict[str, str]:
        """Get Confluent client configuration"""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.security_protocol,
            "sasl.mechanisms": self.sasl_mechanism,
            "sasl.username": self.username,
            "sasl.password": self.password,
            "client.id": self.client_id
        }


class ConfluentKafkaSink(BaseSink, BaseKafkaClient):
    def __init__(self, sink_params: Dict[str, Any]):
        self.params = ConfluentKafkaSinkParams.model_validate(sink_params)
        self.topic = self.params.topic
        super().__init__(self.params.bootstrap_servers)
    
    def get_client_config(self) -> Dict[str, str]:
        return self.params.client_config
    
    def publish(self, data: Dict[str, Any]) -> None:
        self.send_messages(self.topic, [data])

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        self.send_messages(self.topic, data)

    def close(self) -> None:
        pass


class AivenKafkaSinkParams(BaseModel):
    bootstrap_servers: str = Field(..., description="Kafka bootstrap servers")
    topic: str = Field(..., description="Kafka topic to publish to")
    security_protocol: str = Field(default="SASL_SSL", description="Security protocol for Kafka connection")
    sasl_mechanism: str = Field(default="PLAIN", description="SASL mechanism for authentication")
    username: str = Field(..., description="SASL username for authentication")
    password: str = Field(..., description="SASL password for authentication")
    ssl_cafile: str = Field(..., description="Path to SSL CA certificate file")
    client_id: str = Field(default_factory=socket.gethostname, description="Client ID for Kafka connection")
    
    @property
    def client_config(self) -> Dict[str, str]:
        """Get Aiven client configuration"""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.security_protocol,
            "sasl.mechanisms": self.sasl_mechanism,
            "sasl.username": self.username,
            "sasl.password": self.password,
            "client.id": self.client_id,
            "ssl.ca.location": self.ssl_cafile
        }


class AivenKafkaSink(BaseSink, BaseKafkaClient):
    def __init__(self, sink_params: Dict[str, Any]):
        self.params = AivenKafkaSinkParams.model_validate(sink_params)
        self.topic = self.params.topic
        super().__init__(self.params.bootstrap_servers)
    
    def get_client_config(self) -> Dict[str, str]:
        return self.params.client_config
    
    def publish(self, data: Dict[str, Any]) -> None:
        self.send_messages(self.topic, [data])

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        self.send_messages(self.topic, data)

    def close(self) -> None:
        pass
