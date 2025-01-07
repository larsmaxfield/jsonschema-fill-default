import json
from pathlib import Path

from jsonschema import validate, protocols
from jsonref import replace_refs
from jsonschema_fill_default import fill_default


def main():
    # Schema as JSON file, instance as Python dict
    schema_filename = "bicycle.schema.json"
    instance = {
        "style": "road",
        "color": "purple",
        "tire": {
            "width": 28
        }
    }

    # Load schema
    schema_absolute_path = Path(__file__).parent / schema_filename
    with open(schema_absolute_path, 'r') as file:
        schema = json.load(file)

    # Validate schema and validate instance against schema
    protocols.Validator.check_schema(schema)
    validate(instance, schema)

    # De-reference schema "$refs"
    # Assign jsonref.replace_refs return to immediately evaluate and get copy.
    schema = replace_refs(schema)

    # Fill instance with schema defaults
    # fill_default mutates the instance, so we don't assign its return.
    print(f"\nOriginal:\n{json.dumps(instance, indent=4)}")
    fill_default(instance, schema)
    validate(instance, schema)
    print(f"\nFilled:\n{json.dumps(instance, indent=4)}")


if __name__ == "__main__":
    main()
