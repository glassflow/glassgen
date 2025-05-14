from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ValidationError, model_validator


class ConfigError(Exception):
    """Custom exception for configuration errors"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}


def validate_config(config_data: Dict[str, Any]):
    """Validate configuration with graceful error handling"""
    try:
        return GlassGenConfig.model_validate(config_data, context={"parent": None})
    except ValidationError as e:
        errors = []
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            if error["type"] == "extra_forbidden":
                errors.append(f"Unknown field '{loc}'")
            else:
                errors.append(f"Error in {loc}: {msg}")
        raise ConfigError("Configuration validation failed", {"errors": errors}) from e


class SinkConfig(BaseModel):
    type: str
    params: Optional[Dict[str, Any]] = None
    model_config = {"extra": "forbid"}


class DuplicationConfig(BaseModel):
    enabled: bool
    ratio: float = Field(ge=0, le=1)
    key_field: str
    time_window: str = Field(default="1h")
    model_config = {"extra": "forbid"}


class EventOptions(BaseModel):
    duplication: Optional[DuplicationConfig] = None
    model_config = {"extra": "forbid"}


class GeneratorConfig(BaseModel):
    rps: int = Field(default=0, ge=0)
    num_records: int = Field(default=100, ge=-1)
    bulk_size: int = Field(default=5000, ge=0)
    event_options: EventOptions = Field(default=EventOptions())
    model_config = {"extra": "forbid"}


class GlassGenConfig(BaseModel):
    schema_config: Optional[Dict[str, Any]] = Field(alias="schema", default=None)
    sink: Optional[SinkConfig] = None
    generator: GeneratorConfig
    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_duplication(self) -> "GlassGenConfig":
        if (
            self.generator.event_options.duplication
            and self.generator.event_options.duplication.enabled
            and self.generator.event_options.duplication.key_field
            and self.schema_config
        ):
            key_field = self.generator.event_options.duplication.key_field
            if key_field not in self.schema_config:
                raise ValueError(
                    f"key_field '{key_field}' not found in schema. Available fields: "
                    f"{', '.join(self.schema_config.keys())}"
                )
        return self
