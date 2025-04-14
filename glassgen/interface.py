from typing import Dict, Any, Union
import time
from glassgen.schema import BaseSchema
from glassgen.schema.schema import ConfigSchema
from glassgen.sinks import SinkFactory, BaseSink
from glassgen.generator import Generator
from glassgen.config import GlassGenConfig, validate_config, ConfigError


def generate(config: Union[Dict[str, Any], GlassGenConfig], schema: BaseSchema=None, sink: BaseSink = None) -> None:
    """
    Generate data based on the provided configuration.
    
    Args:
        config: Configuration dictionary or GlassGenConfig object
        schema: Optional schema object to use for generating data
        sink: Optional sink object to use for sending generated data
    """
    # Convert dict to Pydantic model if needed
    if isinstance(config, dict):
        try:
            config = validate_config(config)
        except ConfigError as e:
            print("Configuration Error:")
            for error in e.details["errors"]:
                print(f"- {error}")
            exit(1)
            
    # Create schema if not provided
    if schema is None:
        schema = ConfigSchema.from_dict(config.schema_config)
        schema.validate()
    
    # Create sink if not provided
    if sink is None:
        sink = SinkFactory.create(config.sink.type, config.sink.params) 
    
    # Create and run generator    
    generator = Generator(config.generator, schema, sink)
    results = generator.generate()        
    results['sink'] = config.sink.type
    print(results)

    # Close sink
    sink.close()