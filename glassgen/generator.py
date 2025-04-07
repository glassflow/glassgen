import time
from typing import Dict, Any
from faker import Faker
import uuid

from .schema import Schema
from .sinks import BaseSink
from .generators import registry, GeneratorType

class Generator:
    def __init__(self, schema: Schema, sink: BaseSink):
        self.schema = schema
        self.sink = sink
        self.faker = Faker()

    def _generate_record(self) -> Dict[str, Any]:
        record = {}
        for field_name, field in self.schema.fields.items():
            generator = registry.get_generator(field.generator)
            if field.generator == GeneratorType.INTRANGE:
                record[field_name] = generator(min=field.params[0], max=field.params[1])
            else:
                record[field_name] = generator()
        return record

    def generate(self, count: int, rate: int = 0) -> None:
        """
        Generate records and publish them to the sink.
        
        Args:
            count: Number of records to generate
            rate: Records per second (0 for maximum speed)
        """
        try:
            for _ in range(count):
                record = self._generate_record()                
                self.sink.publish(record)
                
                if rate > 0:
                    time.sleep(1.0 / rate)
        finally:
            self.sink.close() 