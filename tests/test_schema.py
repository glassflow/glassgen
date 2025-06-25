from datetime import datetime

import pytest

from glassgen.schema import ConfigSchema
from glassgen.schema.user_schema import UserSchema


def test_basic_schema_generation():
    """Test generation of basic schema fields"""
    schema = ConfigSchema.from_dict(
        {
            "name": "$name",
            "email": "$email",
            "age": "$intrange(18,65)",
            "is_active": "$boolean",
        }
    )

    # Generate a single record
    record = schema._generate_record()

    assert isinstance(record, dict)
    assert "name" in record
    assert "email" in record
    assert "age" in record
    assert "is_active" in record

    # Validate field types
    assert isinstance(record["name"], str)
    assert "@" in record["email"]
    assert 18 <= record["age"] <= 65
    assert isinstance(record["is_active"], bool)


def test_choice_generator():
    """Test the choice generator"""
    schema = ConfigSchema.from_dict(
        {"color": "$choice(red,blue,green)", "number": "$choice(1,2,3)"}
    )

    record = schema._generate_record()

    assert record["color"] in ["red", "blue", "green"]
    assert record["number"] in ["1", "2", "3"]


def test_datetime_generator():
    """Test datetime generator"""
    schema = ConfigSchema.from_dict(
        {"timestamp": "$timestamp", "datetime": "$datetime(%Y-%m-%d %H:%M:%S)"}
    )

    record = schema._generate_record()

    assert isinstance(record["timestamp"], int)
    assert len(str(record["timestamp"])) == 10  # Unix timestamp in seconds

    # Parse and validate datetime string
    try:
        parsed_datetime = datetime.strptime(record["datetime"], "%Y-%m-%d %H:%M:%S")
        # Verify the parsed datetime is not too far from current time
        current_time = datetime.now()
        time_diff = abs((current_time - parsed_datetime).total_seconds())
        assert time_diff < 60  # Should be within 1 minute of current time
    except ValueError as e:
        pytest.fail(f"Failed to parse datetime string: {e}")


def test_uuid_generator():
    """Test UUID generator"""
    schema = ConfigSchema.from_dict({"id": "$uuid", "id4": "$uuid4"})

    record = schema._generate_record()

    # Check UUID format
    assert len(record["id"]) == 36  # Standard UUID length
    assert len(record["id4"]) == 36
    assert record["id"].count("-") == 4
    assert record["id4"].count("-") == 4


def test_predefined_schema():
    """Test using predefined UserSchema"""
    schema = UserSchema()
    record = schema._generate_record()

    # Check all expected fields are present
    expected_fields = {"name", "email", "age", "address", "phone"}

    assert all(field in record for field in expected_fields)

    # Validate some field types
    assert isinstance(record["name"], str)
    assert "@" in record["email"]
    assert isinstance(record["age"], int)
    assert isinstance(record["phone"], str)


def test_flat_schema():
    """Test that flat schemas still work as before"""
    schema_dict = {
        "name": "$name",
        "email": "$email",
        "country": "$country",
        "id": "$uuid",
        "phone": "$phone_number",
        "job": "$job",
        "company": "$company",
        "intrange": "$intrange(10,100)",
        "choice": "$choice(apple,banana,cherry)",
        "weburl": "$url",
        "ts": "$datetime",
        "tsunix": "$timestamp"
    }
    
    schema = ConfigSchema.from_dict(schema_dict)
    schema.validate()
    
    record = schema._generate_record()
    
    # Check that all fields are present
    assert "name" in record
    assert "email" in record
    assert "country" in record
    assert "id" in record
    assert "phone" in record
    assert "job" in record
    assert "company" in record
    assert "intrange" in record
    assert "choice" in record
    assert "weburl" in record
    assert "ts" in record
    assert "tsunix" in record
    
    # Check that intrange is within the specified range
    assert 10 <= record["intrange"] <= 100
    
    # Check that choice is one of the specified values
    assert record["choice"] in ["apple", "banana", "cherry"]


def test_nested_schema():
    """Test that nested schemas work correctly"""
    schema_dict = {
        "name": "$name",
        "email": "$email",
        "country": "$country",
        "id": "$uuid",
        "location": {
            "address": "$address",
            "city": "$city",
            "postal_code": "$zipcode"
        },
        "phone": "$phone_number",
        "job": "$job",
        "company": "$company",
        "intrange": "$intrange(10,100)",
        "choice": "$choice(apple,banana,cherry)",
        "weburl": "$url",
        "ts": "$datetime",
        "tsunix": "$timestamp"
    }
    
    schema = ConfigSchema.from_dict(schema_dict)
    schema.validate()
    
    record = schema._generate_record()
    
    # Check that flat fields are present
    assert "name" in record
    assert "email" in record
    assert "country" in record
    assert "id" in record
    assert "phone" in record
    assert "job" in record
    assert "company" in record
    assert "intrange" in record
    assert "choice" in record
    assert "weburl" in record
    assert "ts" in record
    assert "tsunix" in record
    
    # Check that nested location field is present and has the expected structure
    assert "location" in record
    assert isinstance(record["location"], dict)
    assert "address" in record["location"]
    assert "city" in record["location"]
    assert "postal_code" in record["location"]
    
    # Check that intrange is within the specified range
    assert 10 <= record["intrange"] <= 100
    
    # Check that choice is one of the specified values
    assert record["choice"] in ["apple", "banana", "cherry"]


def test_deeply_nested_schema():
    """Test deeply nested schemas work correctly"""
    schema_dict = {
        "user": {
            "personal": {
                "name": "$name",
                "email": "$email",
                "phone": "$phone_number"
            },
            "address": {
                "street": "$address",
                "city": "$city",
                "country": "$country",
                "postal_code": "$zipcode"
            }
        },
        "metadata": {
            "id": "$uuid",
            "created_at": "$datetime",
            "tags": "$choice(tag1,tag2,tag3)"
        }
    }
    
    schema = ConfigSchema.from_dict(schema_dict)
    schema.validate()
    
    record = schema._generate_record()
    
    # Check nested structure
    assert "user" in record
    assert isinstance(record["user"], dict)
    
    assert "personal" in record["user"]
    assert isinstance(record["user"]["personal"], dict)
    assert "name" in record["user"]["personal"]
    assert "email" in record["user"]["personal"]
    assert "phone" in record["user"]["personal"]
    
    assert "address" in record["user"]
    assert isinstance(record["user"]["address"], dict)
    assert "street" in record["user"]["address"]
    assert "city" in record["user"]["address"]
    assert "country" in record["user"]["address"]
    assert "postal_code" in record["user"]["address"]
    
    assert "metadata" in record
    assert isinstance(record["metadata"], dict)
    assert "id" in record["metadata"]
    assert "created_at" in record["metadata"]
    assert "tags" in record["metadata"]
    assert record["metadata"]["tags"] in ["tag1", "tag2", "tag3"]


def test_mixed_flat_and_nested_schema():
    """Test schemas with both flat and nested fields"""
    schema_dict = {
        "name": "$name",
        "email": "$email",
        "location": {
            "address": "$address",
            "city": "$city"
        },
        "phone": "$phone_number",
        "preferences": {
            "theme": "$choice(dark,light)",
            "notifications": "$choice(true,false)"
        }
    }
    
    schema = ConfigSchema.from_dict(schema_dict)
    schema.validate()
    
    record = schema._generate_record()
    
    # Check flat fields
    assert "name" in record
    assert "email" in record
    assert "phone" in record
    
    # Check nested fields
    assert "location" in record
    assert isinstance(record["location"], dict)
    assert "address" in record["location"]
    assert "city" in record["location"]
    
    assert "preferences" in record
    assert isinstance(record["preferences"], dict)
    assert "theme" in record["preferences"]
    assert "notifications" in record["preferences"]
    assert record["preferences"]["theme"] in ["dark", "light"]
    assert record["preferences"]["notifications"] in ["true", "false"]


def test_invalid_schema_value_type():
    """Test that invalid schema value types raise appropriate errors"""
    schema_dict = {
        "name": "$name",
        "invalid_field": 123  # Invalid type - should be string or dict
    }
    
    with pytest.raises(ValueError, match="Invalid schema value type for field 'invalid_field'"):
        ConfigSchema.from_dict(schema_dict)
