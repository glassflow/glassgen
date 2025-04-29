import glassgen

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
    "sink": {"type": "csv", "params": {"path": "output.csv"}},
    "generator": {"rps": 1500, "num_records": 5000},
}
# Start the generator
print(glassgen.generate(config=config))
