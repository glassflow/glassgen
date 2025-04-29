from typing import Any, Dict, List

from glassgen.sinks.base import BaseSink


class YieldSink(BaseSink):
    def __init__(self, sink_params: Dict[str, Any]):
        pass

    def publish(self, data: Dict[str, Any]):
        yield data

    def publish_bulk(self, data: List[Dict[str, Any]]):
        for item in data:
            yield item

    def close(self) -> None:
        pass
