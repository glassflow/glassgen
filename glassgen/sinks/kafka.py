from confluent_kafka import Producer
import json
import time
from typing import Dict, List

class BaseKafkaClient:
    """Base class for Kafka clients with common functionality"""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer_client = None
        
    def get_client_config(self) -> Dict:
        """Get the configuration for Kafka clients"""
        raise NotImplementedError("Subclasses must implement get_client_config()")
        
    def get_producer_client(self) -> Producer:
        """Get or create producer client"""
        if not self.producer_client:
            client_config = self.get_client_config()
            self.producer_client = Producer(client_config)
        return self.producer_client

    def delivery_report(self, err, msg):
        """Reports message delivery status."""
        if err:
            print(f"❌ Message delivery failed: {err}")
        else:
            pass            
            
    def send_messages(self, topic: str, messages: List[str], delay: int = 0):
        """Send messages to a topic"""
        producer_client = self.get_producer_client()
        for msg in messages:
            message_value = json.dumps(msg) if isinstance(msg, dict) else msg
            producer_client.produce(
                topic,
                value=message_value.encode('utf-8'),
                callback=self.delivery_report
            )
            producer_client.poll(0)  # Trigger message delivery
            if delay:
                time.sleep(delay)

        producer_client.flush()  # Ensure all messages are sent        

