from typing import Dict, Any
from glassgen.schema import BaseSchema
from glassgen.schema.schema import ConfigSchema
from glassgen.sinks import SinkFactory, BaseSink
from glassgen.generator import Generator


def generate(config: Dict[str, Any], schema: BaseSchema=None, sink: BaseSink = None) -> None:
    """
    Generate data based on the provided configuration.
    
    Args:
        config: Configuration dictionary
        schema: Optional schema object to use for generating data
        sink: Optional sink object to use for sending generated data
    """
    # Create schema if not provided
    if schema is None:
        schema = ConfigSchema.from_dict(config["schema"])
        schema.validate()    
    
    # Create sink if not provided
    if sink is None:
        sink = SinkFactory.create(config["sink"]["type"], config["sink"]) 
    
    # Create and run generator
    generator = Generator(schema, sink)
    generator_config = config["generator"]
    
    generator.generate(
        count=generator_config["num_records"],
        rate=generator_config.get("rps", 0)
    ) 