import os

import pytest
import requests

from glassgen.schema import ConfigSchema
from glassgen.sinks import (
    BaseSink,
    CSVSink,
    SinkFactory,
    WebHookSink,
    YieldSink,
)


def test_yield_sink():
    """Test the yield sink"""
    sink = YieldSink({})
    data = {"name": "John", "age": 30}

    # Test single publish
    events = list(sink.publish(data))
    assert len(events) == 1
    assert events[0] == data

    # Test bulk publish
    more_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 35}]
    events = list(sink.publish_bulk(more_data))
    assert len(events) == 2
    assert events == more_data


def test_csv_sink_publish(temp_csv_file):
    """Test the CSV sink publish method"""
    sink = CSVSink({"path": temp_csv_file})
    schema = ConfigSchema.from_dict({"name": "$name", "age": "$intrange(18,65)"})
    data = schema._generate_record()
    sink.publish(data)
    sink.close()

    # Verify CSV file was created and contains data
    assert os.path.exists(temp_csv_file)
    with open(temp_csv_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 2  # Header + 1 data row
        assert "name,age" in lines[0]  # Header

    # Clean up
    os.unlink(temp_csv_file)


def test_csv_sink_bulk_publish(temp_csv_file):
    """Test the CSV sink bulk publish method"""
    sink = CSVSink({"path": temp_csv_file})
    schema = ConfigSchema.from_dict({"name": "$name", "age": "$intrange(18,65)"})

    # Generate and bulk publish some data
    data = [schema._generate_record() for _ in range(3)]
    sink.publish_bulk(data)
    sink.close()

    # Verify CSV file was created and contains data
    assert os.path.exists(temp_csv_file)
    with open(temp_csv_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 4  # Header + 3 data rows
        header = lines[0].strip().split(',')
        assert set(header) == {"name", "age"}  # Header fields, order-agnostic

    # Clean up
    os.unlink(temp_csv_file)


def test_sink_factory():
    """Test the sink factory"""
    # Test CSV sink creation
    csv_sink = SinkFactory.create("csv", {"path": "test.csv"})
    assert isinstance(csv_sink, CSVSink)

    # Test yield sink creation
    yield_sink = SinkFactory.create("yield", {})
    assert isinstance(yield_sink, YieldSink)

    # Test invalid sink type
    with pytest.raises(ValueError):
        SinkFactory.create("invalid_sink", {})


def test_custom_sink():
    """Test creating and using a custom sink"""

    class CustomSink(BaseSink):
        def __init__(self):
            self.events = []
            self.closed = False

        def publish(self, data):
            self.events.append(data)

        def publish_bulk(self, data):
            self.events.extend(data)

        def close(self):
            self.closed = True

    sink = CustomSink()
    data = {"test": "data"}

    # Test single publish
    sink.publish(data)
    assert len(sink.events) == 1
    assert sink.events[0] == data

    # Test bulk publish
    more_data = [{"test": "data1"}, {"test": "data2"}]
    sink.publish_bulk(more_data)
    assert len(sink.events) == 3
    assert sink.events[1:] == more_data

    # Test close
    sink.close()
    assert sink.closed


def test_sink_error_handling():
    """Test sink error handling"""

    class ErrorSink(BaseSink):
        def publish(self, data):
            raise Exception("Test error")

        def publish_bulk(self, data):
            raise Exception("Test bulk error")

        def close(self):
            raise Exception("Test close error")

    sink = ErrorSink()

    # Test error in publish
    with pytest.raises(Exception) as exc_info:
        sink.publish({})
    assert "Test error" in str(exc_info.value)

    # Test error in publish_bulk
    with pytest.raises(Exception) as exc_info:
        sink.publish_bulk([{}])
    assert "Test bulk error" in str(exc_info.value)

    # Test error in close
    with pytest.raises(Exception) as exc_info:
        sink.close()
    assert "Test close error" in str(exc_info.value)


def test_webhook_sink(mock_webhook, webhook_sink_config):
    """Test the webhook sink"""
    # Create webhook sink
    sink = WebHookSink(webhook_sink_config)

    # Test single publish
    data = {"name": "John", "age": 30}
    sink.publish(data)

    # Verify the request was made correctly
    mock_webhook.assert_called_once_with(
        "https://example.com/webhook",
        json=data,
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        timeout=30,
    )

    # Test bulk publish
    more_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 35}]
    sink.publish_bulk(more_data)

    # Verify all requests were made
    assert mock_webhook.call_count == 3  # 1 for single publish + 2 for bulk


def test_webhook_sink_error_handling(mock_webhook, webhook_sink_config):
    """Test webhook sink error handling"""
    # Configure the mock to raise an exception
    mock_webhook.side_effect = requests.exceptions.RequestException("Connection error")

    sink = WebHookSink(webhook_sink_config)

    # Test that exceptions are properly raised
    with pytest.raises(Exception) as exc_info:
        sink.publish({"test": "data"})
    assert "Failed to publish to webhook" in str(exc_info.value)
