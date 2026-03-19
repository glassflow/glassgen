from typing import Any, Dict, Optional, Union
from typing import Generator as PyGenerator

from pydantic import ValidationError

from glassgen.config import ConfigError, GlassGenConfig, SinkConfig, validate_config
from glassgen.generator import Generator
from glassgen.schema import BaseSchema
from glassgen.schema.schema import ConfigSchema
from glassgen.sinks import BaseSink, SinkFactory, YieldSink


def generate_one(schema_dict: Dict[str, Any]):
    schema = ConfigSchema.from_dict(schema_dict)
    schema.validate()
    return schema._generate_record()


def generate(
    config: Union[Dict[str, Any], GlassGenConfig],
    schema: Optional[BaseSchema] = None,
    sink: Optional[Union[BaseSink, Dict[str, Any]]] = None,
) -> Union[Dict[str, Any], PyGenerator[Dict[str, Any], None, Dict[str, Any]]]:
    """
    Generate data based on the provided configuration.

    Args:
        config: Configuration dictionary or GlassGenConfig object
        schema: Optional schema object to use for generating data
        sink: Optional sink object or sink config dict to use for sending generated data

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

    sink_type_name = config.sink.type if config.sink else type(sink).__name__
    if sink is None:
        if config.sink is None:
            raise ConfigError("No sink provided",
          {"errors": ["Sink must be provided either in config or as parameter"]})
        sink = SinkFactory.create(config.sink.type, config.sink.params)
    elif isinstance(sink, dict):
        # Validate sink dict using SinkConfig validator
        try:
            sink_config = SinkConfig.model_validate(sink)
            sink = SinkFactory.create(sink_config.type, sink_config.params)
            sink_type_name = sink_config.type
        except (ValidationError, ConfigError) as e:
            raise ConfigError("Sink validation failed", {"errors": [str(e)]}) from e


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
                response["sink"] = sink_type_name
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

    response["sink"] = sink_type_name
    sink.close()
    return response
