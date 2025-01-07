import json
from pathlib import Path

import pytest
from jsonschema import validate, protocols
from jsonref import replace_refs
from jsonschema_fill_default import fill_default


@pytest.mark.parametrize(
    "schema_filename, instance, expected",
    [(
        "bicycle.schema.json",
        {
            "style": "road",
            "color": "red"
        },
        {
            "style": "road",
            "color": "red",
            "tire-width": 25,
            "front-brake": True,
            "rear-brake": True
        }
    )]
)
def test_load_dereference_fill(schema_filename, instance, expected):
    """Load schema JSON, dereference, fill instance defaults, validate

    This test follows a use case where a schema is loaded from a JSON file,
    dereferenced ($refs replaced), and used to fill a partial JSON instance.

    This test asserts that the filled instance is the expected filled instance.

    This test also validates the following:
    - schema against its meta-schema
    - instance against the schema
    - instance against the dereferenced schema
    - filled instance against the dereferenced schema
    """
    # Load schema
    schema_absolute_path = Path(__file__).parent / schema_filename
    with open(schema_absolute_path, 'r') as file:
        schema = json.load(file)

    # Validate schema and validate instance against schema
    protocols.Validator.check_schema(schema)
    validate(instance, schema)

    # De-reference schema before using it to fill defaults
    # jsonref.replace_refs replaces "$refs" in a schema with the referenced
    # schemas themselves. Assigning its return immediately evaluates it and
    # returns a deep copy.
    schema = replace_refs(schema)
    validate(instance, schema)

    # Fill instance with schema defaults
    # fill_default mutates the instance, so we don't assign its return
    fill_default(instance, schema)
    validate(instance, schema)

    assert instance == expected
