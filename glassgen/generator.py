import time
from glassgen.schema import BaseSchema
from glassgen.sinks import BaseSink

class Generator:
    def __init__(self, schema: BaseSchema, sink: BaseSink):
        self.schema = schema
        self.sink = sink        

    def generate(self, count: int, rate: int = 0) -> None:
        """
        Generate records and publish them to the sink.
        
        Args:
            count: Number of records to generate
            rate: Records per second (0 for maximum speed)
        """
        try:
            for _ in range(count):
                record = self.schema._generate_record()                
                self.sink.publish(record)
                
                if rate > 0:
                    time.sleep(1.0 / rate)
        finally:
            self.sink.close() 