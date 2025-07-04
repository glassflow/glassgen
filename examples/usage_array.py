import glassgen

# Example 1: Basic array generation with simple generators
print("=== Example 1: Basic ARRAY usage ===")
config_basic = {
    "schema": {
        "user_id": "$prefixed_id(user, 1, 1000)",
        "emails": "$array(email, 3)",
        "names": "$array(name, 2)",
        "phone_numbers": "$array(phone_number, 2)"
    },
    "generator": {"num_records": 3},
    "sink": {"type": "csv", "params": {"path": "output_arrays_basic.csv"}}
}

gen_basic = glassgen.generate(config=config_basic)
for row in gen_basic:
    print(row)

# Example 2: Array with generators that have parameters
print("\n=== Example 2: ARRAY with parameterized generators ===")
config_params = {
    "schema": {
        "product_id": "$prefixed_id(prod, 1, 100)",
        "prices": "$array(price, 5)",
        "quantities": "$array(intrange, 5, 1, 50)",
        "categories": "$array(choice, 3, electronics, clothing, books, sports, home)"
    },
    "generator": {"num_records": 3},
    "sink": {"type": "csv", "params": {"path": "output_arrays_params.csv"}}
}

gen_params = glassgen.generate(config=config_params)
for row in gen_params:
    print(row)

# Example 3: Mixed arrays and single values
print("\n=== Example 3: Mixed arrays and single values ===")
config_mixed = {
    "schema": {
        "order_id": "$prefixed_id(order, 1000, 9999)",
        "customer_name": "$name",
        "order_date": "$datetime",
        "product_ids": "$array(prefixed_id, 3, prod, 1, 100)",
        "quantities": "$array(intrange, 3, 1, 10)",
        "total_amount": "$price"
    },
    "generator": {"num_records": 3},
    "sink": {"type": "csv", "params": {"path": "output_arrays_mixed.csv"}}
}

gen_mixed = glassgen.generate(config=config_mixed)
for row in gen_mixed:
    print(row)

# Example 4: Nested schema with arrays
print("\n=== Example 4: Nested schema with arrays ===")
config_nested = {
    "schema": {
        "store": {
            "store_id": "$prefixed_id(store, 1, 50)",
            "store_name": "$company",
            "manager_emails": "$array(email, 2)"
        },
        "products": {
            "product_ids": "$array(prefixed_id, 4, prod, 1, 1000)",
            "product_names": "$array(company, 4)",
            "prices": "$array(price, 4)"
        },
        "revenue": "$price"
    },
    "generator": {"num_records": 2},
    "sink": {"type": "csv", "params": {"path": "output_arrays_nested.csv"}}
}

gen_nested = glassgen.generate(config=config_nested)
for row in gen_nested:
    print(row) 