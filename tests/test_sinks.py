import pytest
import tempfile
import os
import json
import csv
from glassgen.sinks import CSVSink, JSONSink, KafkaSink

def test_csv_sink():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        sink = CSVSink(tmp_path)
        
        # Test first record (should create header)
        sink.publish({"name": "John", "age": 30})
        
        # Test second record
        sink.publish({"name": "Jane", "age": 25})
        
        sink.close()
        
        # Verify file contents
        with open(tmp_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 2
            assert rows[0]["name"] == "John"
            assert rows[0]["age"] == "30"
            assert rows[1]["name"] == "Jane"
            assert rows[1]["age"] == "25"
            
    finally:
        os.unlink(tmp_path)

def test_json_sink():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        sink = JSONSink(tmp_path)
        
        # Test multiple records
        sink.publish({"name": "John", "age": 30})
        sink.publish({"name": "Jane", "age": 25})
        
        sink.close()
        
        # Verify file contents
        with open(tmp_path, 'r') as f:
            data = json.load(f)
            
            assert len(data) == 2
            assert data[0]["name"] == "John"
            assert data[0]["age"] == 30
            assert data[1]["name"] == "Jane"
            assert data[1]["age"] == 25
            
    finally:
        os.unlink(tmp_path)

def test_kafka_sink():
    # Note: This test requires a running Kafka instance
    # You might want to skip this test in CI/CD environments
    pytest.skip("Kafka tests require a running Kafka instance")
    
    sink = KafkaSink(
        bootstrap_servers="localhost:9092",
        topic="test_topic"
    )
    
    try:
        # Test publishing a record
        sink.publish({"name": "John", "age": 30})
    finally:
        sink.close() 