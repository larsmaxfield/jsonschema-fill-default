import sys
import json

from jsonschema import validate, ValidationError, SchemaError
from jsonref import replace_refs
from jsonschema_fill_default import fill_default


def main():
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

    # 2. De-reference (fill schema references)
    schema = replace_refs(schema)  # replace_refs returns copy with refs fill

    # 3. Fill instance with schema defaults
    print(f"Original:\n{instance}\n")
    fill_default(instance, schema)  # fill_default mutates instance
    print(f"Filled:\n{instance}\n")


if __name__ == "__main__":
    main()
