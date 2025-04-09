from typing import Dict, Any, Union
import time
from glassgen.schema import BaseSchema
from glassgen.schema.schema import ConfigSchema
from glassgen.sinks import SinkFactory, BaseSink
from glassgen.generator import Generator
from glassgen.config import GlassGenConfig


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
        config = GlassGenConfig(**config)
    
    # Create schema if not provided
    if schema is None:
        schema = ConfigSchema.from_dict(config.schema_config)
        schema.validate()
    
    # Create sink if not provided
    if sink is None:
        sink = SinkFactory.create(config.sink.type, config.sink.params) 
    
    # Create and run generator
    start_time = time.time()
    generator = Generator(config.generator, schema, sink)
    generator.generate()
    end_time = time.time()
    time_taken_ms = round((end_time - start_time)*1000)
    #print(f"Time taken: {time_taken_ms} milliseconds")
    print(f"Generated {config.generator.num_records} records and published to {config.sink.type} in {time_taken_ms} milliseconds")

    # Close sink
    sink.close()