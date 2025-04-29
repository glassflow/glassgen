from glassgen.sinks.base import BaseSink
from glassgen.sinks.csv_sink import CSVSink
from glassgen.sinks.kafka_sink import KafkaSink
from glassgen.sinks.webhook_sink import WebHookSink
from glassgen.sinks.yield_sink import YieldSink

__all__ = [
    "BaseSink",
    "CSVSink",
    "SinkFactory",
    "KafkaSink",
    "WebHookSink",
    "YieldSink",
]


class SinkFactory:
    _sinks = {
        "csv": CSVSink,
        "webhook": WebHookSink,
        "yield": YieldSink,
        "kafka": KafkaSink,
    }

    @classmethod
    def create(cls, class_type: str, sink_config: dict):
        if class_type not in cls._sinks:
            raise ValueError(f"Unknown class_type: {class_type}")
        return cls._sinks[class_type](sink_config)
