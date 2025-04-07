import pytest
import tempfile
import os
from glassgen.generator import Generator
from glassgen.schema import Schema
from glassgen.sinks import CSVSink

def test_generator_creation():
    schema = Schema.from_dict({
        "name": "$string",
        "age": "$intrange(18, 65)"
    })
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        sink = CSVSink(tmp_path)
        generator = Generator(schema, sink)
        
        assert generator.schema == schema
        assert generator.sink == sink
        assert "string" in generator._generators
        assert "intrange" in generator._generators
        
    finally:
        os.unlink(tmp_path)

def test_record_generation():
    schema = Schema.from_dict({
        "name": "$string",
        "age": "$intrange(18, 65)"
    })
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        sink = CSVSink(tmp_path)
        generator = Generator(schema, sink)
        
        # Generate a single record
        record = generator._generate_record()
        
        assert "name" in record
        assert "age" in record
        assert isinstance(record["name"], str)
        assert isinstance(record["age"], int)
        assert 18 <= record["age"] <= 65
        
    finally:
        os.unlink(tmp_path)

def test_generator_with_rate():
    schema = Schema.from_dict({
        "name": "$string",
        "age": "$intrange(18, 65)"
    })
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        sink = CSVSink(tmp_path)
        generator = Generator(schema, sink)
        
        # Generate 5 records at 10 records per second
        import time
        start_time = time.time()
        generator.generate(5, rate=10)
        end_time = time.time()
        
        # Should take approximately 0.5 seconds (5 records at 10 per second)
        assert 0.4 <= (end_time - start_time) <= 0.6
        
        # Verify records were written
        with open(tmp_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 5
            
    finally:
        os.unlink(tmp_path) 