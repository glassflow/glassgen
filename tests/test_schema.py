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


def test_prefixed_id_generator():
    """Test PREFIXED_ID generator"""
    # Test with default parameters
    schema_default = ConfigSchema.from_dict({"id": "$prefixed_id"})
    record_default = schema_default._generate_record()
    
    # Check format: prefix_number
    assert "id" in record_default
    assert "_" in record_default["id"]
    prefix, number = record_default["id"].split("_")
    assert prefix == "item"  # default prefix
    assert number.isdigit()
    assert 1 <= int(number) <= 1000  # default range
    
    # Test with custom prefix and range
    schema_custom = ConfigSchema.from_dict({
        "product_id": "$prefixed_id(prod, 1, 100)",
        "category_id": "$prefixed_id(cat, 10, 50)"
    })
    record_custom = schema_custom._generate_record()
    
    # Check product_id format
    assert "product_id" in record_custom
    assert record_custom["product_id"].startswith("prod_")
    prod_prefix, prod_number = record_custom["product_id"].split("_")
    assert prod_prefix == "prod"
    assert prod_number.isdigit()
    assert 1 <= int(prod_number) <= 100
    
    # Check category_id format
    assert "category_id" in record_custom
    assert record_custom["category_id"].startswith("cat_")
    cat_prefix, cat_number = record_custom["category_id"].split("_")
    assert cat_prefix == "cat"
    assert cat_number.isdigit()
    assert 10 <= int(cat_number) <= 50
    
    # Test with different ranges
    schema_ranges = ConfigSchema.from_dict({
        "user_id": "$prefixed_id(user, 1000, 9999)",
        "order_id": "$prefixed_id(order, 1, 1000)"
    })
    record_ranges = schema_ranges._generate_record()
    
    # Check user_id range
    user_prefix, user_number = record_ranges["user_id"].split("_")
    assert user_prefix == "user"
    assert 1000 <= int(user_number) <= 9999
    
    # Check order_id range
    order_prefix, order_number = record_ranges["order_id"].split("_")
    assert order_prefix == "order"
    assert 1 <= int(order_number) <= 1000


def test_prefixed_id_generator_registry():
    """Test that PREFIXED_ID generator is properly registered"""
    from glassgen.generator.generators import registry, GeneratorType
    
    # Check that the generator is registered
    assert GeneratorType.PREFIXED_ID in registry.get_supported_generators()
    
    # Get the generator function
    generator_func = registry.get_generator(GeneratorType.PREFIXED_ID)
    assert callable(generator_func)
    
    # Test the generator function directly
    result = generator_func("test", 1, 10)
    assert result.startswith("test_")
    prefix, number = result.split("_")
    assert prefix == "test"
    assert number.isdigit()
    assert 1 <= int(number) <= 10
    
    # Test with default parameters
    result_default = generator_func()
    assert result_default.startswith("item_")
    prefix, number = result_default.split("_")
    assert prefix == "item"
    assert number.isdigit()
    assert 1 <= int(number) <= 1000


def test_array_generator():
    """Test ARRAY generator"""
    # Test with simple generator (no parameters)
    schema_simple = ConfigSchema.from_dict({
        "emails": "$array(email, 3)",
        "names": "$array(name, 2)"
    })
    record_simple = schema_simple._generate_record()
    
    # Check emails array
    assert "emails" in record_simple
    assert isinstance(record_simple["emails"], list)
    assert len(record_simple["emails"]) == 3
    for email in record_simple["emails"]:
        assert isinstance(email, str)
        assert "@" in email
    
    # Check names array
    assert "names" in record_simple
    assert isinstance(record_simple["names"], list)
    assert len(record_simple["names"]) == 2
    for name in record_simple["names"]:
        assert isinstance(name, str)
        assert " " in name  # Names typically have spaces
    
    # Test with generator that has parameters
    schema_with_params = ConfigSchema.from_dict({
        "numbers": "$array(intrange, 5, 1, 100)",
        "choices": "$array(choice, 3, apple, banana, cherry)"
    })
    record_with_params = schema_with_params._generate_record()
    
    # Check numbers array
    assert "numbers" in record_with_params
    assert isinstance(record_with_params["numbers"], list)
    assert len(record_with_params["numbers"]) == 5
    for num in record_with_params["numbers"]:
        assert isinstance(num, int)
        assert 1 <= num <= 100
    
    # Check choices array
    assert "choices" in record_with_params
    assert isinstance(record_with_params["choices"], list)
    assert len(record_with_params["choices"]) == 3
    for choice in record_with_params["choices"]:
        assert choice in ["apple", "banana", "cherry"]


def test_array_generator_registry():
    """Test that ARRAY generator is properly registered"""
    from glassgen.generator.generators import registry, GeneratorType
    
    # Check that the generator is registered
    assert GeneratorType.ARRAY in registry.get_supported_generators()
    
    # Get the generator function
    generator_func = registry.get_generator(GeneratorType.ARRAY)
    assert callable(generator_func)
    
    # Test the generator function directly
    result = generator_func("email", 3)
    assert isinstance(result, list)
    assert len(result) == 3
    for email in result:
        assert isinstance(email, str)
        assert "@" in email
    
    # Test with parameters
    result_with_params = generator_func("intrange", 2, 10, 20)
    assert isinstance(result_with_params, list)
    assert len(result_with_params) == 2
    for num in result_with_params:
        assert isinstance(num, int)
        assert 10 <= num <= 20


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
        "tsunix": "$timestamp",
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
        "location": {"address": "$address", "city": "$city", "postal_code": "$zipcode"},
        "phone": "$phone_number",
        "job": "$job",
        "company": "$company",
        "intrange": "$intrange(10,100)",
        "choice": "$choice(apple,banana,cherry)",
        "weburl": "$url",
        "ts": "$datetime",
        "tsunix": "$timestamp",
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
            "personal": {"name": "$name", "email": "$email", "phone": "$phone_number"},
            "address": {
                "street": "$address",
                "city": "$city",
                "country": "$country",
                "postal_code": "$zipcode",
            },
        },
        "metadata": {
            "id": "$uuid",
            "created_at": "$datetime",
            "tags": "$choice(tag1,tag2,tag3)",
        },
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
        "location": {"address": "$address", "city": "$city"},
        "phone": "$phone_number",
        "preferences": {
            "theme": "$choice(dark,light)",
            "notifications": "$choice(true,false)",
        },
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
        "invalid_field": 123,  # Invalid type - should be string or dict
    }

    with pytest.raises(
        ValueError, match="Invalid schema value type for field 'invalid_field'"
    ):
        ConfigSchema.from_dict(schema_dict)
