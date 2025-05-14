import time
from typing import Any, Dict, List

from glassgen.config import GeneratorConfig
from glassgen.generator.batch_controller import DynamicBatchController
from glassgen.generator.duplication import DuplicateController
from glassgen.schema import BaseSchema


class Generator:
    def __init__(self, generator_config: GeneratorConfig, schema: BaseSchema):
        self.generator_config = generator_config
        self.schema = schema
        self.batch_controller = (
            DynamicBatchController(self.generator_config.rps)
            if self.generator_config.rps > 0
            else None
        )
        self.max_bulk_size = generator_config.bulk_size
        self.duplicate_controller = (
            DuplicateController(self.generator_config)
            if self.generator_config.event_options.duplication
            else None
        )

    def _generate_batch(self, num_records: int) -> List[Dict[str, Any]]:
        records = []
        for _ in range(num_records):
            record = None
            if self.duplicate_controller:
                record = self.duplicate_controller._get_if_duplication()
            if record is None:
                record = self.schema._generate_record()
                if self.duplicate_controller:
                    self.duplicate_controller.add_record(record)
            records.append(record)
        return records

    def generate(self):
        """
        Generate records and publish them to the sink.
        """
        start_time = time.time()
        count = 0
        events_to_send = self.generator_config.num_records
        if events_to_send == -1:
            events_to_send = float("inf")
        else:
            events_to_send = int(events_to_send)

        while True:
            batch_size = (
                self.batch_controller.get_batch_size(self.max_bulk_size)
                if self.batch_controller
                else min(self.max_bulk_size, events_to_send - count)
            )
            actual_batch_size = min(batch_size, events_to_send - count)
            records = self._generate_batch(actual_batch_size)
            count += len(records)

            yield records

            if self.batch_controller:
                self.batch_controller.record_sent(actual_batch_size)

            if count >= events_to_send:
                break

        response = {
            "time_taken_ms": round((time.time() - start_time) * 1000),
            "num_records": count,
        }
        if self.duplicate_controller:
            response.update(self.duplicate_controller.get_results())
        return response
