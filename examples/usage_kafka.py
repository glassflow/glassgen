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
        "company": "$company"
    },
    "sink": {
        "type": "kafka.aiven",
        "bootstrap_servers": "broker.h.aivencloud.com:12766",
        "username": "default",
        "password": "******",
        "ssl_cafile": "ca.pem",
        "topic": "example",
        "security_protocol": "SASL_SSL",
        "sasl_mechanism": "SCRAM-SHA-256"                
    },
    "generator": {
        "rps": 1500,
        "num_records": 50
    }
} 

print(glassgen.generate(config=config))