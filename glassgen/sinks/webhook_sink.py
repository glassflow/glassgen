import requests
from typing import List, Dict, Any
from .base import BaseSink

class WebHookSink(BaseSink):
    """
    A sink that sends data to a webhook URL using HTTP POST requests.
    """
    def __init__(self, sink_params: Dict[str, Any]):
        """
        Initialize the WebHook sink.
        
        Args:
            sink_config (Dict[str, Any]): Configuration dictionary containing:
                - type: "webhook"
                - params: {
                    "url": str,
                    "headers": Dict[str, str] (optional),
                    "timeout": int (optional, defaults to 30)
                }
        """
        self.url = sink_params.get("url")
        if not self.url:
            raise ValueError("Webhook URL is required in sink configuration")
            
        self.headers = sink_params.get("headers", {})
        self.timeout = sink_params.get("timeout", 30)
        
        # Ensure content-type is set
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = 'application/json'

    def publish(self, record: Dict[str, Any]) -> None:
        """
        Publish a single record to the webhook URL.
        
        Args:
            record (Dict[str, Any]): The record to publish
        """
        try:
            response = requests.post(
                self.url,
                json=record,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to publish to webhook: {str(e)}")

    def publish_bulk(self, records: List[Dict[str, Any]]) -> None:
        """
        Publish multiple records to the webhook URL.
        
        Args:
            records (List[Dict[str, Any]]): List of records to publish
        """
        for record in records:
            self.publish(record)

    def close(self) -> None:
        pass