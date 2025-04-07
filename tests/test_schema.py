import pytest
from glassgen.schema import Schema, SchemaField

def test_schema_from_dict():
    schema_dict = {
        "name": "$string",
        "age": "$intrange(18, 65)",
        "email": "$email"
    }
    
    schema = Schema.from_dict(schema_dict)
    
    assert len(schema.fields) == 3
    assert schema.fields["name"].generator == "string"
    assert schema.fields["age"].generator == "intrange"
    assert schema.fields["age"].params == [18, 65]
    assert schema.fields["email"].generator == "email"

def test_schema_validation():
    # Test valid schema
    valid_schema = Schema.from_dict({
        "name": "$string",
        "age": "$intrange(18, 65)",
        "email": "$email"
    })
    valid_schema.validate()  # Should not raise any exception

    # Test invalid generator
    invalid_schema = Schema.from_dict({
        "name": "$invalid_generator"
    })
    with pytest.raises(ValueError, match="Unsupported generator"):
        invalid_schema.validate()

    # Test invalid intrange parameters
    invalid_intrange = Schema.from_dict({
        "age": "$intrange(18)"  # Missing max parameter
    })
    with pytest.raises(ValueError, match="requires exactly 2 parameters"):
        invalid_intrange.validate()

def test_schema_field_creation():
    field = SchemaField(name="test", generator="string")
    assert field.name == "test"
    assert field.generator == "string"
    assert field.params == []

    field_with_params = SchemaField(name="age", generator="intrange", params=[18, 65])
    assert field_with_params.params == [18, 65] 