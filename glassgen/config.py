from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class SinkConfig(BaseModel):
    type: str
    params: Optional[Dict[str, Any]] = None

class GeneratorConfig(BaseModel):
    rps: int = Field(default=0, ge=0)
    # can be set to -1 to generate indefinitely
    num_records: int = Field(default=100, ge=-1)
    # bulk size for some sinks
    bulk_size: int = Field(default=100, ge=0)

class GlassGenConfig(BaseModel):
    schema_config: Dict[str, Any] = Field(alias="schema")
    sink: SinkConfig
    generator: GeneratorConfig 