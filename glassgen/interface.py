from typing import Dict, Any
from glassgen.schema import BaseSchema
from glassgen.schema.schema import ConfigSchema
from glassgen.sinks import CSVSink, JSONSink, KafkaSink, BaseSink
from glassgen.generator import Generator

def create_sink(config: Dict[str, Any]) -> Any:
    """Create a sink based on the configuration"""
    print(f"Creating sink from config: {config}")
    sink_config = config["sink"]
    sink_type = sink_config["type"]
    
    if sink_type == "csv":
        return CSVSink(sink_config["path"])
    elif sink_type == "json":
        return JSONSink(sink_config["path"])
    elif sink_type == "kafka":
        return KafkaSink(
            bootstrap_servers=sink_config["bootstrap_servers"],
            topic=sink_config["topic"]
        )
    else:
        raise ValueError(f"Unsupported sink type: {sink_type}")

def generate(config: Dict[str, Any], schema: BaseSchema = None, sink: BaseSink = None) -> None:
    """
    Generate data based on the provided configuration.
    
    Args:
        config: Configuration dictionary with the following structure:
            {
                "schema": {
                    "field1": "$generator_type",
                    "field2": "$generator_type(param1, param2)",
                    ...
                },
                "sink": {
                    "type": "csv|json|kafka",
                    "path": "output.csv",  # for csv/json
                    "bootstrap_servers": "localhost:9092",  # for kafka
                    "topic": "topic_name"  # for kafka
                },
                "generator": {
                    "rps": 1000,  # records per second
                    "num_records": 5000  # total number of records to generate
                }
            }
    """
    # Create schema
    if schema is None:
        schema = ConfigSchema.from_dict(config["schema"])
        schema.validate()        
    
    if sink is None:
        sink = create_sink(config)            
    # Create and run generator
    generator = Generator(schema, sink)
    generator_config = config["generator"]
    
    print(f"Generating {generator_config['num_records']} records at {generator_config.get('rps', 0)} records per second")
    print(f"Starting generation...")
    generator.generate(
        count=generator_config["num_records"],
        rate=generator_config.get("rps", 0)
    ) 