import pytest
from jsonschema import validate, Draft202012Validator
from jsonschema_fill_default import fill_default


# List of schemas, instances, and filled instances tuples
# for each test case (empty props, partial props, filled, anyOf, etc.)

test_schemas_instances = {
    "properties": {
        "schema": {
            "title": "JSON Schema of 'properties' with defaults",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "properties": {
                "someString": {"default": "The default string"},
                "someInteger": {"default": 9},
                "someArray": {"default": ["A", 1]},
                "someObject": {
                    "properties": {
                        "someNumber": {"default": 3.14},
                        "someBoolean": {"default": True}
                    }
                }
            },
            "additionalProperties": False,
            "unevaluatedProperties": False
        },
        "instances": [
            {  # Empty
                "original": {},
                "expected": {
                    "someString": "The default string",
                    "someInteger": 9,
                    "someArray": ["A", 1],
                    "someObject": {
                        "someNumber": 3.14,
                        "someBoolean": True
                    }
                }
            },
            {  # Partial
                "original": {
                    "someString": "An existing string",
                    "someObject": {
                        "someNumber": 1234567.89,
                    }
                },
                "expected": {
                    "someString": "An existing string",
                    "someInteger": 9,
                    "someArray": ["A", 1],
                    "someObject": {
                        "someNumber": 1234567.89,
                        "someBoolean": True
                    }
                }
            },
            {  # Full
                "original": {
                    "someString": "Hello",
                    "someInteger": -100,
                    "someArray": ["Z", 26],
                    "someObject": {
                        "someNumber": 0.123,
                        "someBoolean": False
                    }
                },
                "expected": {
                    "someString": "Hello",
                    "someInteger": -100,
                    "someArray": ["Z", 26],
                    "someObject": {
                        "someNumber": 0.123,
                        "someBoolean": False
                    }
                }
            },
        ]
    },
    "allOf": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'allOf' with defaults",
            "type": "object",
            "allOf": [
                {"properties": {"someInteger": {"default": 9}}},
                {"properties": {"someBoolean": {"default": True}}}
            ]
        },
        "instances": [
            {  # Empty
                "original": {},
                "expected": {
                    "someInteger": 9,
                    "someBoolean": True
                }
            },
            {  # Partial
                "original": {
                    "someInteger": -100
                },
                "expected": {
                    "someInteger": -100,
                    "someBoolean": True
                }
            },
            {  # Full
                "original": {
                    "someInteger": -100,
                    "someBoolean": False
                },
                "expected": {
                    "someInteger": -100,
                    "someBoolean": False
                }
            },
        ]
    },
    "if-then": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'if-then' with conditional default",
            "type": "object",
            "if": {
                "required": ["someBoolean"]
            },
            "then": {"properties": {
                "conditionalString": {"default": "someBoolean was given"}
            }}
        },
        "instances": [
            {  # Empty
                "original": {},
                "expected": {}
            },
            {  # Then
                "original": {
                    "someBoolean": True
                },
                "expected": {
                    "someBoolean": True,
                    "conditionalString": "someBoolean was given"
                }
            }
        ]
    },
    "if-then-else": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of nested 'if-then-else' with defaults",
            "type": "object",
            "if": {
                "required": ["someInteger"]
            },
            "then": {
                "if": {
                    "properties": {
                        "someInteger": {"multipleOf": 2}
                    }
                },
                "then": {"properties": {
                    "conditionalString": {"default": "Even integer"}
                }},
                "else": {"properties": {
                    "conditionalString": {"default": "Odd integer"}
                }}
            },
            "else": {"properties": {
                "conditionalString": {"default": "No integer given"}
            }}
        },
        "instances": [
            {  # Empty
                "original": {},
                "expected": {"conditionalString": "No integer given"}
            },
            {  # Then
                "original": {
                    "someInteger": 16
                },
                "expected": {
                    "someInteger": 16,
                    "conditionalString": "Even integer"
                }
            },
            {  # Else
                "original": {
                    "someInteger": -9
                },
                "expected": {
                    "someInteger": -9,
                    "conditionalString": "Odd integer"
                }
            },
        ]
    },
    # "allOf-if-then-else": {
    #     "schema": {
    #         "$schema": "https://json-schema.org/draft/2020-12/schema",
    #         "title": "JSON Schema of 'allOf' with defaults",
    #         "type": "object",
    #         "allOf": [
    #             {
    #                 "if": {"properties": {"someString": {"const": "abc"}}},
    #                 "then": {"properties": {
    #                     "conditionalNumber": {"type": "number", "default": 69},
    #                 }}
    #             },
    #             {
    #                 "if": {"properties": {"someString": {"const": "xyz"}}},
    #                 "then": {"properties": {
    #                     "conditionalObject": {
    #                         "type": "object",
    #                         "default": {
    #                             "someString": "goodbye",
    #                             "someNumber": -100
    #                         }
    #                     }
    #                 }}
    #             }
    #         ]
    #     }
    # },
}


schemas = test_schemas_instances.values()

instance_schema_pairs = []
for test in test_schemas_instances.values():
    for instance in test["instances"]:
        instance_schema_pairs.append((instance["original"], test["schema"]))
        instance_schema_pairs.append((instance["expected"], test["schema"]))

original_schema_expected_triplets = []
for test in test_schemas_instances.values():
    for instance in test["instances"]:
        original_schema_expected_triplets.append((
            instance["original"],
            test["schema"],
            instance["expected"]
        ))


# All schemas must be valid to their meta-schema
@pytest.mark.parametrize(
    "schema",
    schemas
)
def test_schema_is_valid_meta_schema(schema):
    assert Draft202012Validator.check_schema(schema) is None


# All instances must be valid to their schema
@pytest.mark.parametrize(
    "instance, schema",
    instance_schema_pairs
)
def test_instance_is_valid_schema(instance, schema):
    assert validate(instance, schema) is None


# All filled instances must equal their expected
@pytest.mark.parametrize(
    "original, schema, expected",
    original_schema_expected_triplets
)
def test_filled_instance_is_equal_to_expected(original, schema, expected):
    fill_default(original, schema)
    assert original == expected
