# GlassGen

GlassGen is a flexible synthetic data generation service that can generate data based on user-defined schemas and send it to various destinations.

## Features

- Generate synthetic data based on custom schemas
- Multiple output formats (CSV, Kafka, Webhook)
- Configurable generation rate
- Extensible sink architecture
- CLI and Python SDK interfaces

## Installation

```bash
pip install glassgen
```

### Local Development Installation

1. Clone the repository:
```bash
git clone https://github.com/glassflow/glassgen.git
cd glassgen
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Run tests to verify installation:
```bash
pytest
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
        "type": "csv|kafka|webhook",
        "params": {
            // sink-specific parameters
        }
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
        "params": {
            "path": "output.csv"
        }
    }
}
```

### WebHook Sink
```json
{
    "sink": {
        "type": "webhook",
        "params": {
            "url": "https://your-webhook-url.com",
            "headers": {
                "Authorization": "Bearer your-token",
                "Custom-Header": "value"
            },
            "timeout": 30  // optional, defaults to 30 seconds
        }
    }
}
```

### Kafka Sink
GlassGen supports multiple Kafka sink types:

1. **Confluent Cloud**
```json
{
    "sink": {
        "type": "kafka.confluent",
        "params": {
            "bootstrap_servers": "your-confluent-bootstrap-server",
            "topic": "topic_name",
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
            "sasl_plain_username": "your-api-key",
            "sasl_plain_password": "your-api-secret"
        }
    }
}
```

2. **Aiven Kafka**
```json
{
    "sink": {
        "type": "kafka.aiven",
        "params": {
            "bootstrap_servers": "your-aiven-bootstrap-server",
            "topic": "topic_name",
            "security_protocol": "SASL_SSL",
            "sasl.mechanisms": "SCRAM-SHA-256",
            "ssl_cafile": "path/to/ca.pem"
        }
    }
}
```

## Supported Schema Generators

### Basic Types
- `$string`: Random string
- `$int`: Random integer
- `$intrange(min,max)`: Random integer within specified range (e.g., `$intrange(1,100)` for numbers between 1 and 100)
- `$choice(value1,value2,...)`: Randomly picks one value from the provided list (e.g., `$choice(red,blue,green)` or `$choice(1,2,3,4,5)`)
- `$datetime`: Current timestamp in ISO format (e.g., "2024-03-15T14:30:45.123456")
- `$timestamp`: Current Unix timestamp in seconds since epoch (e.g., 1710503445)
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
        "email": "$email",
        "country": "$country",
        "id": "$uuid",
        "address": "$address",
        "phone": "$phone_number",
        "job": "$job",
        "company": "$company"
    },
    "sink": {
        "type": "webhook",
        "params": {
            "url": "https://api.example.com/webhook",
            "headers": {
                "Authorization": "Bearer your-token"
            }
        }
    },
    "generator": {
        "rps": 1500,
        "num_records": 5000
    }
}
```

## Creating a New Release

To create a new release:

1. Make sure you have the release script installed:
```bash
pip install -e .
```

2. Run the release script with the new version:
```bash
./scripts/release.py release 0.1.1
```

This will:
- Update the version in pyproject.toml
- Create a git tag
- Push the changes
- Trigger the GitHub Actions workflow to:
  - Build the package
  - Publish to PyPI
  - Create a GitHub release

The version must follow semantic versioning (X.Y.Z format).
