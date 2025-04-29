from typing import Any, Dict, List

import requests
from pydantic import BaseModel, Field

from .base import BaseSink


class WebHookSinkParams(BaseModel):
    url: str = Field(..., description="Webhook URL to send data to")
    headers: Dict[str, str] = Field(
        default_factory=dict, description="HTTP headers for the request"
    )
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")


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
        params = WebHookSinkParams.model_validate(sink_params)
        self.url = params.url
        self.headers = params.headers
        self.timeout = params.timeout

        # Ensure content-type is set
        if "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "application/json"

    def publish(self, record: Dict[str, Any]) -> None:
        """
        Publish a single record to the webhook URL.

        Args:
            record (Dict[str, Any]): The record to publish
        """
        try:
            response = requests.post(
                self.url, json=record, headers=self.headers, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to publish to webhook: {str(e)}") from e

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
