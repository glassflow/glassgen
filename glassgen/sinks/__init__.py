from glassgen.sinks.base import BaseSink
from glassgen.sinks.csv_sink import CSVSink
from glassgen.sinks.json_sink import JSONSink
from glassgen.sinks.kafka_sink import ConfluentKafkaSink
from glassgen.sinks.kafka_sink import AivenKafkaSink    

__all__ = ["BaseSink", "CSVSink", "JSONSink", "SinkFactory", "ConfluentKafkaSink", "AivenKafkaSink"]


class SinkFactory:
    _sinks = {
        "csv": CSVSink,
        "json": JSONSink,
        "confluent_kafka": ConfluentKafkaSink,
        "aiven_kafka": AivenKafkaSink,
    }

    @classmethod
    def create(cls, class_type: str, sink_config: dict):
        if class_type not in cls._sinks:
            raise ValueError(f"Unknown class_type: {class_type}")
        return cls._sinks[class_type](sink_config)
