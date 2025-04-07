import re
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field
from .generators import GeneratorType, registry

class SchemaField(BaseModel):
    name: str
    generator: str
    params: List[Any] = Field(default_factory=list)

class Schema(BaseModel):
    fields: Dict[str, SchemaField]

    @classmethod
    def from_dict(cls, schema_dict: Dict[str, str]) -> "Schema":
        fields = {}
        for name, generator_str in schema_dict.items():
            # Parse generator string like "$intrange(1, 100)" or "$string"
            match = re.match(r"\$(\w+)(?:\((.*)\))?", generator_str)
            if not match:
                raise ValueError(f"Invalid generator format: {generator_str}")
            
            generator_name = match.group(1)
            params_str = match.group(2)
            
            params = []
            if params_str:
                # Simple parameter parsing - can be enhanced for more complex cases
                params = [p.strip() for p in params_str.split(",")]
                # Convert numeric parameters
                params = [int(p) if p.isdigit() else p for p in params]
            
            fields[name] = SchemaField(
                name=name,
                generator=generator_name,
                params=params
            )
        
        return cls(fields=fields)

    def validate(self) -> None:
        """Validate that all generators are supported"""
        supported_generators = set(registry.get_supported_generators().keys())
        
        for field in self.fields.values():
            if field.generator not in supported_generators:
                raise ValueError(
                    f"Unsupported generator: {field.generator}. "
                    f"Supported generators are: {', '.join(supported_generators)}"
                )
            
            if field.generator == GeneratorType.INTRANGE and len(field.params) != 2:
                raise ValueError(
                    "$intrange generator requires exactly 2 parameters (min, max)"
                ) 