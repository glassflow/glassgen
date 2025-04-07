# usage of a custom sink
from print_sink import PrintSink
import glassgen
import json

sink = PrintSink()

with open("config.json") as f:
    config_json = json.load(f)

glassgen.generate(config=config_json, sink=sink)