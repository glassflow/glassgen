import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from glassgen.generator.generators import GeneratorType, registry
from glassgen.schema.base import BaseSchema


class SchemaField(BaseModel):
    name: str
    generator: str
    params: List[Any] = Field(default_factory=list)


class ConfigSchema(BaseSchema, BaseModel):
    """Schema implementation that can be created from a configuration"""

    fields: Dict[str, SchemaField]

    @classmethod
    def from_dict(cls, schema_dict: Dict[str, str]) -> "ConfigSchema":
        """Create a schema from a configuration dictionary"""
        fields = cls._schema_dict_to_fields(schema_dict)
        return cls(fields=fields)

    @staticmethod
    def _schema_dict_to_fields(schema_dict: Dict[str, str]) -> Dict[str, SchemaField]:
        """Convert a schema dictionary to a dictionary of SchemaField objects"""
        fields = {}
        for name, generator_str in schema_dict.items():
            match = re.match(r"\$(\w+)(?:\((.*)\))?", generator_str)
            if not match:
                raise ValueError(f"Invalid generator format: {generator_str}")

            generator_name = match.group(1)
            params_str = match.group(2)

            params = []
            if params_str:
                # Handle choice generator specially
                if generator_name == GeneratorType.CHOICE:
                    # Split by comma but preserve quoted strings
                    params = [p.strip().strip("\"'") for p in params_str.split(",")]

                else:
                    # Simple parameter parsing for other generators
                    params = [p.strip() for p in params_str.split(",")]
                    # Convert numeric parameters
                    params = [int(p) if p.isdigit() else p for p in params]

            fields[name] = SchemaField(
                name=name, generator=generator_name, params=params
            )
        return fields

    def validate(self) -> None:
        """Validate that all generators are supported"""
        supported_generators = set(registry.get_supported_generators().keys())

        for field in self.fields.values():
            if field.generator not in supported_generators:
                raise ValueError(
                    f"Unsupported generator: {field.generator}. "
                    f"Supported generators are: {', '.join(supported_generators)}"
                )

    def _generate_record(self) -> Dict[str, Any]:
        """Generate a single record based on the schema"""
        record = {}
        for field_name, field in self.fields.items():
            generator = registry.get_generator(field.generator)
            # Pass parameters to the generator if they exist
            if field.params:
                if field.generator == GeneratorType.CHOICE:
                    # For choice generator, pass the list directly
                    record[field_name] = generator(field.params)
                else:
                    # For other generators, unpack the parameters
                    record[field_name] = generator(*field.params)
            else:
                record[field_name] = generator()
        return record
