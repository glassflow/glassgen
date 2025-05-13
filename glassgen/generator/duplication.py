import copy
import random
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple


class DuplicateController:
    def __init__(self, generator_config):
        self.generator_config = generator_config
        self.duplicates: deque[Tuple[datetime, Dict[str, Any]]] = deque()
        self.total_generated = 0
        self.total_duplicates = 0
        self.time_window = self._parse_time_window(
            self.generator_config.event_options.duplication.time_window
        )
        self.target_ratio = self.generator_config.event_options.duplication.ratio
        self.max_size = 1000  # You can make this configurable too

    def _parse_time_window(self, time_window: str) -> timedelta:
        """Convert time_window string to timedelta"""
        value = int(time_window[:-1])
        unit = time_window[-1]
        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
        else:
            raise ValueError(f"Invalid time window unit: {unit}")

    def _cleanup_old_duplicates(self):
        """Remove duplicates older than time_window"""
        cutoff_time = datetime.now() - self.time_window
        while self.duplicates and self.duplicates[0][0] < cutoff_time:
            self.duplicates.popleft()

    def _get_if_duplication(self):
        current_ratio = self.total_duplicates / max(1, self.total_generated)
        if current_ratio >= self.target_ratio:
            return None
        else:
            duplicate = self._get_duplicate()
            if duplicate is not None:
                self.total_duplicates += 1
                return duplicate

    def _get_duplicate(self):
        """Get a random duplicate from the stored records"""
        self._cleanup_old_duplicates()
        if not self.duplicates:
            return None
        return random.choice([record for _, record in self.duplicates])

    def add_record(self, record: Dict[str, Any]):
        """Add a record to the deque with timestamp, enforce max size"""
        now = datetime.now()
        self.duplicates.append((now, copy.deepcopy(record)))
        self.total_generated += 1

        # Trim to max size
        if len(self.duplicates) > self.max_size:
            self.duplicates.popleft()

    def get_results(self):
        return {
            "total_generated": self.total_generated,
            "total_duplicates": self.total_duplicates,
            "duplication_ratio": round(
                self.total_duplicates / max(1, self.total_generated), 2
            ),
        }
