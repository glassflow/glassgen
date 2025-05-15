import time


class DynamicBatchController:
    def __init__(self, target_rps: int):
        self.target_rps = target_rps
        self.last_reset = time.time()
        self.records_sent = 0
        self.window = 1.0  # seconds

    def get_batch_size(self, max_batch_size: int) -> int:
        now = time.time()
        elapsed = now - self.last_reset

        if elapsed >= self.window:
            self._reset(now)

        remaining_time = self.window - elapsed
        remaining_records = max(self.target_rps - self.records_sent, 0)
        if remaining_time <= 0 or remaining_records <= 0:
            self._sleep_until_next_window()
            return self.get_batch_size(max_batch_size)
        # estimate the batch size based on the remaining records and the target RPS
        est_batch = int(remaining_records)
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
