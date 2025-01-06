import sys
import json

from jsonschema import validate, ValidationError, SchemaError
from jsonref import replace_refs
from jsonschema_fill_default import fill_default


def main():
    # TODO: Rewrite examples with test examples for clarity
    # TODO: Readme examples from simple to complex, with section "Using $refs?"

    # schema_filename = 'allof.example.schema.json'
    # instance = {
    #     "someString": "AAA"
    # }

    schema_filename = 'examples/oneof.example.schema.json'
    instance = {
        "someString": "B"
    }

    # schema_filename = 'examples/example.schema.json'
    # instance = {
    #     "someObject": {
    #         "someString": "abc"
    #     }
    # }

    with open(schema_filename, 'r') as file:
        schema = json.load(file)

    # # 1. Validate initial
    try:
        validate(instance, schema)
    except ValidationError:
        print("Instance not valid against schema")
        sys.exit(1)
    except SchemaError:
        print("Schema not valid")
        sys.exit(1)
    else:
        print("Schema and instance valid")

    # 2. De-reference
    # Replace $refs in schema with referenced schemas themselves.
    schema = replace_refs(schema)  # jsonref.replace_refs with return to copy

    # 3. Fill instance with schema defaults
    print(f"Original:\n{instance}\n")
    fill_default(instance, schema)  # fill_default without return (mutates)
    print(f"Filled:\n{instance}\n")


if __name__ == "__main__":
    main()
