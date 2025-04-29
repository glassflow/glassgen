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
    "sink": {
        "type": "kafka",
        "params": {
            "bootstrap.servers": "broker.h.aivencloud.com:12766",
            "topic": "example",
            "sasl.username": "default",
            "sasl.password": "******",
            "ssl.ca.location": "ca.pem",
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "SCRAM-SHA-256",
        },
    },
    "generator": {"rps": 1500, "num_records": 50},
}

print(glassgen.generate(config=config))
