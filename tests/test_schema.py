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
