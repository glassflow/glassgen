from typing import Any, Dict, Optional, Union
from typing import Generator as PyGenerator

from glassgen.config import ConfigError, GlassGenConfig, validate_config
from glassgen.generator import Generator
from glassgen.schema import BaseSchema
from glassgen.schema.schema import ConfigSchema
from glassgen.sinks import BaseSink, SinkFactory, YieldSink


def generate(
    config: Union[Dict[str, Any], GlassGenConfig],
    schema: Optional[BaseSchema] = None,
    sink: Optional[BaseSink] = None,
) -> Union[Dict[str, Any], PyGenerator[Dict[str, Any], None, Dict[str, Any]]]:
    """
    Generate data based on the provided configuration.

    Args:
        config: Configuration dictionary or GlassGenConfig object
        schema: Optional schema object to use for generating data
        sink: Optional sink object to use for sending generated data

    Returns:
        If using a yield sink: A generator that yields events
        Otherwise: A dictionary containing the final response
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
    generator = Generator(config.generator, schema)
    gen = generator.generate()

    # If using a yield sink, return a generator
    if isinstance(sink, YieldSink):

        def event_generator():
            try:
                while True:
                    events = next(gen)
                    for event in events:
                        yield event
            except StopIteration as e:
                response = e.value
                response["sink"] = config.sink.type
                sink.close()
                return response

        return event_generator()

    # For regular sinks, process all events and return final response
    try:
        while True:
            events = next(gen)
            sink.publish_bulk(events)
    except StopIteration as e:
        response = e.value

    response["sink"] = config.sink.type
    sink.close()
    return response
