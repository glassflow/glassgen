import glassgen
from glassgen.schema.user_schema import UserSchema

config = {
    "sink": {"type": "csv", "params": {"path": "output.csv"}},
    "generator": {"rps": 1500, "num_records": 5000},
}

print(glassgen.generate(config=config, schema=UserSchema()))
