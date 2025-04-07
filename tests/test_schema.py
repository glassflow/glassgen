import pytest
from glassgen.schema import Schema, SchemaField

def test_schema_from_dict():
    schema_dict = {
        "name": "$string",
        "email": "$email"
    }
    
    schema = Schema.from_dict(schema_dict)
    
    assert len(schema.fields) == 3
    assert schema.fields["name"].generator == "string"
    assert schema.fields["email"].generator == "email"

def test_schema_validation():
    # Test valid schema
    valid_schema = Schema.from_dict({
        "name": "$string",
        "email": "$email"
    })
    valid_schema.validate()  # Should not raise any exception

    # Test invalid generator
    invalid_schema = Schema.from_dict({
        "name": "$invalid_generator"
    })
    with pytest.raises(ValueError, match="Unsupported generator"):
        invalid_schema.validate()

def test_schema_field_creation():
    field = SchemaField(name="test", generator="string")
    assert field.name == "test"
    assert field.generator == "string"
    assert field.params == []
