# GlassGen

GlassGen is a flexible synthetic data generation service that can generate data based on user-defined schemas and send it to various destinations.

## Features

- Generate synthetic data based on custom schemas
- Multiple output formats (CSV, JSON, Kafka)
- Configurable generation rate
- Extensible sink architecture
- CLI and Python SDK interfaces
- MCP server for AI-assisted data generation

## Installation

```bash
pip install glassgen
```

## Usage

### Basic Usage

```python
import glassgen
import json

# Load configuration from file
with open("config.json") as f:
    config = json.load(f)

# Start the generator
glassgen.generate(config=config)
```

### Configuration File Format

```json
{
    "schema": {
        "field1": "$generator_type",
        "field2": "$generator_type(param1, param2)"
    },
    "sink": {
        "type": "csv|json|kafka",
        "path": "output.csv",  // for csv/json
        "bootstrap_servers": "localhost:9092",  // for kafka
        "topic": "topic_name"  // for kafka
    },
    "generator": {
        "rps": 1000,  // records per second
        "num_records": 5000  // total number of records to generate
    }
}
```

## Supported Sinks

### CSV Sink
```json
{
    "sink": {
        "type": "csv",
        "path": "output.csv"
    }
}
```

### JSON Sink
```json
{
    "sink": {
        "type": "json",
        "path": "output.json"
    }
}
```

### Kafka Sink
```json
{
    "sink": {
        "type": "kafka",
        "bootstrap_servers": "localhost:9092",
        "topic": "topic_name"
    }
}
```

## Supported Schema Generators

### Basic Types
- `$string`: Random string
- `$int`: Random integer
- `$intrange(min, max)`: Random integer within range
- `$boolean`: Random boolean value
- `$uuid`: Random UUID
- `$uuid4`: Random UUID4

### Personal Information
- `$name`: Random full name
- `$email`: Random email address
- `$company_email`: Random company email
- `$user_name`: Random username
- `$password`: Random password
- `$phone_number`: Random phone number
- `$ssn`: Random Social Security Number

### Location
- `$country`: Random country name
- `$city`: Random city name
- `$address`: Random street address
- `$zipcode`: Random zip code

### Business
- `$company`: Random company name
- `$job`: Random job title
- `$url`: Random URL

### Other
- `$text`: Random text paragraph
- `$ipv4`: Random IPv4 address
- `$currency_name`: Random currency name
- `$color_name`: Random color name

## Example Configuration

```json
{
    "schema": {
        "name": "$name",
        "age": "$intrange(18, 65)",
        "email": "$email",
        "country": "$country",
        "id": "$uuid",
        "address": "$address",
        "phone": "$phone_number",
        "job": "$job",
        "company": "$company"
    },
    "sink": {
        "type": "csv",
        "path": "output.csv"
    },
    "generator": {
        "rps": 1500,
        "num_records": 5000
    }
}
```

## Extending GlassGen

You can create custom sinks by implementing the `BaseSink` interface:

```python
from glassgen.sinks import BaseSink

class CustomSink(BaseSink):
    def publish(self, data):
        # Implement your custom publishing logic
        pass
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
``` 