import pytest
from glassgen.schema import Schema

@pytest.fixture
def sample_schema():
    return Schema.from_dict({
        "name": "$string",
        "age": "$intrange(18, 65)",
        "email": "$email",
        "country": "$country",
        "id": "$uuid"
    })

@pytest.fixture
def sample_config():
    return {
        "schema": {
            "name": "$string",
            "age": "$intrange(18, 65)",
            "email": "$email"
        },
        "sink": {
            "type": "csv",
            "path": "test_output.csv"
        },
        "generation": {
            "count": 100,
            "rate": 10
        }
    } 