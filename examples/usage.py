import glassgen

config = {
    "schema": {"name": "$name", "user": {"email": "$email", "id": "$uuid"}},
    "generator": {"num_records": 10},
}
sink_csv = {"type": "csv", "params": {"path": "output.csv"}}
config["sink"] = sink_csv

gen = glassgen.generate(config=config)
for row in gen:
    print(row)
