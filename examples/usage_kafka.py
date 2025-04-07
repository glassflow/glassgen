# usage of a custom sink
import glassgen
import json
from glassgen.schema import UserSchema

with open("config.kafka.json") as f:
    config_json = json.load(f)

glassgen.generate(config=config_json, schema=UserSchema())