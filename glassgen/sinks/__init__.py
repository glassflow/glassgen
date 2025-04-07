from glassgen.sinks.base import BaseSink
from glassgen.sinks.csv_sink import CSVSink
from glassgen.sinks.kafka_sink import ConfluentKafkaSink
from glassgen.sinks.kafka_sink import AivenKafkaSink
from glassgen.sinks.webhook_sink import WebHookSink

__all__ = ["BaseSink", "CSVSink", "SinkFactory", "ConfluentKafkaSink", "AivenKafkaSink", "WebHookSink"]


class SinkFactory:
    _sinks = {
        "csv": CSVSink,
        "kafka.confluent": ConfluentKafkaSink,
        "kafka.aiven": AivenKafkaSink,
        "webhook": WebHookSink,
    }

    @classmethod
    def create(cls, class_type: str, sink_config: dict):
        if class_type not in cls._sinks:
            raise ValueError(f"Unknown class_type: {class_type}")
        return cls._sinks[class_type](sink_config)
