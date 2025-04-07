from typing import Any, Dict, List
from glassgen.sinks.base import BaseSink
from glassgen.sinks.kafka import BaseKafkaClient
import socket

    
class ConfluentKafkaSink(BaseSink, BaseKafkaClient):
    def __init__(self, sink_params: dict):
        self.sink_params = sink_params                
        bootstrap_servers = self.sink_params['bootstrap_servers']
        self.username = self.sink_params['username']
        self.password = self.sink_params['password']
        self.topic = self.sink_params['topic']

        super().__init__(bootstrap_servers)

    def get_client_config(self) -> Dict:
        """Get Confluent client configuration"""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.sink_params['security_protocol'],
            "sasl.mechanisms": self.sink_params['sasl_mechanism'],
            "sasl.username": self.sink_params['sasl_plain_username'],
            "sasl.password": self.sink_params['sasl_plain_password'],
            "client.id": socket.gethostname()
        }
    
    def publish(self, data: Dict[str, Any]) -> None:
        self.send_messages(self.topic, [data])

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        self.send_messages(self.topic, data)

    def close(self) -> None:
        pass


class AivenKafkaSink(BaseSink, BaseKafkaClient):
    def __init__(self, sink_config: dict):
        self.sink_config = sink_config
        bootstrap_servers = self.sink_config['bootstrap_servers']
        self.username = self.sink_config['username']
        self.password = self.sink_config['password']
        self.ca_cert = self.sink_config['ssl_cafile']
        self.topic = self.sink_config['topic']

        super().__init__(bootstrap_servers)
        
    def publish(self, data: Dict[str, Any]) -> None:
        self.send_messages(self.topic, [data])

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        self.send_messages(self.topic, data)

    def close(self) -> None:
        pass

    def get_client_config(self) -> Dict:
        """Get Aiven client configuration""" 
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.sink_config['security_protocol'],
            "sasl.mechanisms": self.sink_config['sasl_mechanism'],
            "sasl.username": self.username,
            "sasl.password": self.password,
            "client.id": socket.gethostname(),            
            "ssl.ca.location": self.ca_cert
        }
