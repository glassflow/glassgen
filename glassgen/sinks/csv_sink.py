import csv
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from glassgen.sinks.base import BaseSink


class CSVSinkParams(BaseModel):
    path: str = Field(..., description="Path to the output CSV file")


class CSVSink(BaseSink):
    def __init__(self, sink_params: Dict[str, Any]):
        params = CSVSinkParams.model_validate(sink_params)
        self.filepath = Path(params.path)
        self.writer = None
        self.file = None
        self.fieldnames = None

    def _flatten_dict(
        self, data: Dict[str, Any], parent_key: str = "", sep: str = "_"
    ) -> Dict[str, Any]:
        """
        Flatten a nested dictionary by concatenating keys with separator.

        Args:
            data: The dictionary to flatten
            parent_key: The parent key prefix
            sep: Separator to use between nested keys

        Returns:
            Flattened dictionary with concatenated keys
        """
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)

    def _get_flattened_fieldnames(self, data: List[Dict[str, Any]]) -> List[str]:
        """
        Get fieldnames from flattened data to ensure consistent column order.

        Args:
            data: List of dictionaries to process

        Returns:
            List of fieldnames for CSV header
        """
        all_keys = set()
        for item in data:
            flattened = self._flatten_dict(item)
            all_keys.update(flattened.keys())
        return sorted(list(all_keys))

    def publish(self, data: Dict[str, Any]) -> None:
        # Flatten the data before writing
        flattened_data = self._flatten_dict(data)

        if self.writer is None:
            self.file = open(self.filepath, "w", newline="")
            self.fieldnames = list(flattened_data.keys())
            self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
            self.writer.writeheader()

        self.writer.writerow(flattened_data)

    def publish_bulk(self, data: List[Dict[str, Any]]) -> None:
        if self.writer is None:
            self.file = open(self.filepath, "w", newline="")
            # Get fieldnames from all data to ensure consistent columns
            self.fieldnames = self._get_flattened_fieldnames(data)
            self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
            self.writer.writeheader()

        # Flatten each record before writing
        flattened_data = [self._flatten_dict(item) for item in data]
        self.writer.writerows(flattened_data)

    def close(self) -> None:
        if self.file:
            self.file.close()
