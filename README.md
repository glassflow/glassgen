# GlassGen

<p align="left">
  <a target="_blank" href="https://pypi.python.org/pypi/glassgen">
    <img src="https://img.shields.io/pypi/v/glassgen.svg?labelColor=&color=e69e3a">
  </a>
  <a target="_blank" href="https://github.com/astral-sh/glassgen/blob/main/LICENSE">
    <img src="https://img.shields.io/pypi/l/glassgen.svg?labelColor=&color=e69e3a">
  </a>
  <a target="_blank" href="https://pypi.python.org/pypi/glassgen">
    <img src="https://img.shields.io/pypi/pyversions/glassgen.svg?labelColor=&color=e69e3a">
  </a>
  <br />
  <a target="_blank" href="(https://github.com/glassflow/glassgen/actions">
    <img src="https://github.com/glassflow/glassgen/workflows/Test/badge.svg?labelColor=&color=e69e3a">
  </a>
<!-- Pytest Coverage Comment:Begin -->
  <img src=https://img.shields.io/badge/coverage-93%25-brightgreen>
<!-- Pytest Coverage Comment:End -->
</p>


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
        "type": "csv|kafka|webhook|yield",
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

GlassGen supports multiple sink types for different output destinations:

- [CSV Sink](#csv-sink) - Write data to CSV files
- [Kafka Sink](#kafka-sink) - Send data to Kafka topics (supports both Confluent Cloud and Aiven)
- [Webhook Sink](#webhook-sink) - Send data to HTTP endpoints
- [Yield Sink](#yield-sink) - Get data as an iterator in Python
- [Custom Sink](#custom-sink) - Create your own sink implementation

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
The Kafka sink uses the `confluent_kafka` Python package to connect to any Kafka cluster. It accepts all configuration parameters supported by the package:

```json
{
    "sink": {
        "type": "kafka",
        "params": {
            "bootstrap.servers": "your-kafka-bootstrap-server",
            "topic": "topic_name",
            "security.protocol": "SASL_SSL",  // optional
            "sasl.mechanism": "PLAIN",        // optional
            "sasl.username": "your-api-key",  // optional
            "sasl.password": "your-api-secret" // optional
        }
    }
}
```

The minimum required parameters are `bootstrap.servers` and `topic`. Any additional configuration parameters supported by the `confluent_kafka` package can be added to the params object.

### Yield Sink
Yield sink returns an iterator for the generated events
```json
{
    "sink" : {
        "type": "yield"
    }
}
```
#### Usage 
```python
config = {
    "schema": {
        "name": "$name",        
        "email": "$email"
    },
    "sink": {
        "type": "yield"
    },
    "generator": {
        "rps": 100,
        "num_records": 1000
    }
}  

import glassgen
gen = glassgen.generate(config=config)
for item in gen:
    print(item)
```


### Custom Sink
You can create your own sink by extending the `BaseSink` class:

```python
from glassgen import generate
from glassgen.sinks import BaseSink
from typing import List

class PrintSink(BaseSink):
    def publish(self, data: str):
        print(data)
    
    def publish_bulk(self, data: List[str]):
        for d in data:
            self.publish(d)
    
    def close(self):
        pass

# Use your custom sink
config = {
    "schema": {
        "name": "$name",
        "email": "$email",
        "country": "$country",
        "id": "$uuid",        
    },    
    "generator": {
        "rps": 10,
        "num_records": 1000        
    }
}
generate(config, sink=PrintSink())
```

## Supported Schema Generators

### Basic Types
- `$string`: Random string
- `$int`: Random integer
- `$intrange(min,max)`: Random integer within specified range (e.g., `$intrange(1,100)` for numbers between 1 and 100)
- `$choice(value1,value2,...)`: Randomly picks one value from the provided list (e.g., `$choice(red,blue,green)` or `$choice(1,2,3,4,5)`)
- `$datetime(format)`: Current timestamp in specified format (e.g., `$datetime(%Y-%m-%d %H:%M:%S)`). Default format is ISO format (e.g., "2024-03-15T14:30:45.123456")
- `$timestamp`: Current Unix timestamp in seconds since epoch (e.g., 1710503445)
- `$boolean`: Random boolean value
- `$uuid`: Random UUID
- `$uuid4`: Random UUID4
- `$float`: Random floating point number
- `$price`: Random price value with 2 decimal places (e.g., 99.99)

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


### Pre Defined Schema
You can use of of the pre-defined schema:

```python
import glassgen
from glassgen.schema.user_schema import UserSchema

config = {
    "sink": {
        "type": "csv",
        "params": {
            "path": "output.csv"
        }
    },
    "generator": {
        "rps": 50,
        "num_records": 100
    }
}
# use the pre-defined UserSchema
glassgen.generate(config=config, schema=UserSchema())
```

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
        "num_records": 5000,
        "event_options": {
            "duplication": {
                "enabled": true,
                "ratio": 0.1,
                "key_field": "email",
                "time_window": "1h"
            }
        }
    }
}
```

## Event Options

### Duplication

GlassGen supports controlled event duplication to simulate real-world scenarios where the same event might be processed multiple times.

```json
"event_options": {
    "duplication": {
        "enabled": true,        // Enable/disable duplication
        "ratio": 0.1,          // Target ratio of duplicates (0.0 to 1.0)
        "key_field": "email",  // Field to use for duplicate detection
        "time_window": "1h"    // Time window for duplicate detection
    }
}
```

- `enabled`: Boolean to turn duplication on/off
- `ratio`: Decimal value (0.0 to 1.0) representing the percentage of events that should be duplicates
- `key_field`: Field name from the schema to use for identifying duplicates
- `time_window`: String representing the time window for duplicate detection (e.g., "1h" for 1 hour, "30m" for 30 minutes)

The duplication feature:
- Maintains the specified ratio across all generated events
- Only considers events within the configured time window for duplication
- Uses the specified key_field to identify potential duplicates
- Ensures memory efficiency by automatically cleaning up old events

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
