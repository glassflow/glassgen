# usage of a custom sink
import glassgen
from glassgen.sinks import BaseSink


# a sink that prints the data to the console
class PrintSink(BaseSink):
    def __init__(self, config=None):
        self.config = config

    def publish(self, data):
        print(data)

    def publish_bulk(self, data):
        for item in data:
            print(item)

    def close(self):
        pass


config = {
    "schema": {
        "name": "$name",
        "email": "$email",
        "country": "$country",
        "id": "$uuid",
        "address": "$address",
        "phone": "$phone_number",
        "job": "$job",
        "company": "$company",
    },
    "generator": {"rps": 10, "num_records": 100},
}

print(glassgen.generate(config=config, sink=PrintSink()))
