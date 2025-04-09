import time
from glassgen.schema import BaseSchema
from glassgen.sinks import BaseSink
from glassgen.config import GeneratorConfig

class DynamicBatchController:
    def __init__(self, target_rps: int):
        self.target_rps = target_rps
        self.last_reset = time.time()
        self.records_sent = 0
        self.window = 1.0  # seconds

    def get_batch_size(self, max_batch_size: int = 1000) -> int:
        now = time.time()
        elapsed = now - self.last_reset

        if elapsed >= self.window:
            self._reset(now)

        remaining_time = self.window - elapsed
        remaining_records = max(self.target_rps - self.records_sent, 0)

        if remaining_time <= 0 or remaining_records <= 0:
            self._sleep_until_next_window()
            return self.get_batch_size(max_batch_size)

        est_batch = int(remaining_records * 0.1)
        batch_size = min(est_batch or 1, remaining_records, max_batch_size)
        return max(1, batch_size)

    def record_sent(self, count: int):
        self.records_sent += count
        self._sleep_if_needed()

    def _reset(self, now):
        self.last_reset = now
        self.records_sent = 0

    def _sleep_if_needed(self):
        now = time.time()
        elapsed = now - self.last_reset
        expected_time = self.records_sent / self.target_rps
        if expected_time > elapsed:
            sleep_time = expected_time - elapsed
            time.sleep(sleep_time)

    def _sleep_until_next_window(self):
        now = time.time()
        sleep_time = self.window - (now - self.last_reset)
        if sleep_time > 0:
            time.sleep(sleep_time)
        self._reset(time.time())


class Generator:
    def __init__(self, generator_config: GeneratorConfig, schema: BaseSchema, sink: BaseSink):
        self.generator_config = generator_config
        self.schema = schema
        self.sink = sink
        self.batch_controller = (
            DynamicBatchController(self.generator_config.rps) if self.generator_config.rps > 0 else None
        )
        self.max_bulk_size = 5000

    def _generate_batch(self, num_records: int):
        records = []
        for _ in range(num_records):
            records.append(self.schema._generate_record())
        return records

    def generate(self) -> None:
        """
        Generate records and publish them to the sink.    
        """
        count = 0
        events_to_send = self.generator_config.num_records
        if events_to_send == -1:
            events_to_send = float('inf')
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
            #print(f"Generated {len(records)}. Total records generated: {count} out of {events_to_send}")
            if len(records) > 1:
                self.sink.publish_bulk(records)
            else:
                self.sink.publish(records[0])
            
            if self.batch_controller:
                self.batch_controller.record_sent(actual_batch_size)
                
            if count >= events_to_send:
                break