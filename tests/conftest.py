import tempfile
from unittest.mock import Mock, patch

import pytest

from glassgen.config import DuplicationConfig, EventOptions, GeneratorConfig
from glassgen.sinks import BaseSink


@pytest.fixture
def basic_config():
    return {
        "schema": {"name": "$name", "email": "$email", "age": "$intrange(18,65)"},
        "sink": {"type": "csv", "params": {"path": "test_output.csv"}},
        "generator": {"rps": 100, "num_records": 10},
    }


@pytest.fixture
def yield_sink_config():
    return {
        "schema": {"name": "$name", "email": "$email"},
        "sink": {"type": "yield"},
        "generator": {"rps": 100, "num_records": 5},
    }


@pytest.fixture
def duplication_config():
    return {
        "schema": {"name": "$name", "email": "$email", "id": "$uuid"},
        "sink": {"type": "yield"},
        "generator": {
            "rps": 100,
            "num_records": 10,
            "event_options": {
                "duplication": {
                    "enabled": True,
                    "ratio": 0.2,
                    "key_field": "email",
                    "time_window": "1h",
                }
            },
        },
    }


@pytest.fixture
def mock_sink():
    class MockSink(BaseSink):
        def __init__(self):
            self.events = []
            self.closed = False

        def publish(self, data: dict):
            self.events.append(data)

        def publish_bulk(self, data: list):
            self.events.extend(data)

        def close(self):
            self.closed = True

    return MockSink()


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        return f.name


@pytest.fixture
def mock_webhook():
    """Fixture for mocking webhook requests"""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_kafka():
    """Fixture for mocking kafka producer"""
    with patch("confluent_kafka.Producer") as mock_producer_class:
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer
        yield mock_producer


@pytest.fixture
def webhook_sink_config():
    """Fixture for webhook sink configuration"""
    return {
        "url": "https://example.com/webhook",
        "headers": {"Authorization": "Bearer token"},
        "timeout": 30,
    }


@pytest.fixture
def kafka_sink_config():
    """Fixture for kafka sink configuration"""
    return {"bootstrap.servers": "localhost:9092", "topic": "test-topic"}


@pytest.fixture
def generator_config():
    """Fixture for generator configuration with duplication enabled"""
    return GeneratorConfig(
        rps=100,
        num_records=1000,
        event_options=EventOptions(
            duplication=DuplicationConfig(
                enabled=True,
                ratio=0.2,
                key_field="id",
                time_window="1h"
            )
        )
    )
