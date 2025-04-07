# usage of a custom sink
import glassgen
import json
from glassgen.schema.user_schema import UserSchema

with open("config.json") as f:
    config_json = json.load(f)

print(f"Config: {config_json}")
glassgen.generate(config=config_json, schema=UserSchema())