import re
from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

from glassgen.generator.generators import GeneratorType, registry
from glassgen.schema.base import BaseSchema


class SchemaField(BaseModel):
    name: str
    generator: str
    params: List[Any] = Field(default_factory=list)


class NestedSchemaField(BaseModel):
    """Represents a nested schema field that contains other fields"""

    name: str
    fields: Dict[str, Union[SchemaField, "NestedSchemaField"]]


class ConfigSchema(BaseSchema, BaseModel):
    """Schema implementation that can be created from a configuration"""

    fields: Dict[str, Union[SchemaField, NestedSchemaField]]

    @classmethod
    def from_dict(cls, schema_dict: Dict[str, Any]) -> "ConfigSchema":
        """Create a schema from a configuration dictionary"""
        fields = cls._schema_dict_to_fields(schema_dict)
        return cls(fields=fields)

    @staticmethod
    def _schema_dict_to_fields(
        schema_dict: Dict[str, Any],
    ) -> Dict[str, Union[SchemaField, NestedSchemaField]]:
        """Convert a schema dictionary to a dictionary of SchemaField or
        NestedSchemaField objects"""
        fields = {}
        for name, value in schema_dict.items():
            if isinstance(value, dict):
                # Handle nested structure
                nested_fields = ConfigSchema._schema_dict_to_fields(value)
                fields[name] = NestedSchemaField(name=name, fields=nested_fields)
            elif isinstance(value, str):
                # Handle flat generator string
                match = re.match(r"\$(\w+)(?:\((.*)\))?", value)
                if not match:
                    raise ValueError(f"Invalid generator format: {value}")

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
            else:
                raise ValueError(
                    f"Invalid schema value type for field '{name}': {type(value)}"
                )
        return fields

    def validate(self) -> None:
        """Validate that all generators are supported"""
        supported_generators = set(registry.get_supported_generators().keys())

        def validate_fields(
            fields_dict: Dict[str, Union[SchemaField, NestedSchemaField]],
        ):
            for field in fields_dict.values():
                if isinstance(field, SchemaField):
                    if field.generator not in supported_generators:
                        raise ValueError(
                            f"Unsupported generator: {field.generator}. "
                            f"Supported generators are: "
                            f"{', '.join(supported_generators)}"
                        )
                elif isinstance(field, NestedSchemaField):
                    validate_fields(field.fields)

        validate_fields(self.fields)

    def _generate_record(self) -> Dict[str, Any]:
        """Generate a single record based on the schema"""

        def generate_nested_record(
            fields_dict: Dict[str, Union[SchemaField, NestedSchemaField]],
        ) -> Dict[str, Any]:
            record = {}
            for field_name, field in fields_dict.items():
                if isinstance(field, SchemaField):
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
                elif isinstance(field, NestedSchemaField):
                    record[field_name] = generate_nested_record(field.fields)
            return record

        return generate_nested_record(self.fields)
