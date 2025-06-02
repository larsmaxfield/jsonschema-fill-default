import pytest
from jsonschema import validate, protocols
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
    "rootDefault": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema with 'default' at root",
            "type": "object",
            "properties": {
                "pool": {
                    "properties": {
                        "max_connections": {"type": "integer"},
                        "min_connections": {"type": "integer"}
                    }
                }
            },
            "default": {
                "pool": {
                    "max_connections": 8,
                    "min_connections": 0
                }
            },
            "additionalProperties": False,
            "unevaluatedProperties": False
        },
        "instances": [
            {  # Empty
                "original": {},
                "expected": {
                    "pool": {
                        "max_connections": 8,
                        "min_connections": 0
                    }
                }
            },
            {  # Partial
                "original": {
                    "pool": {
                        "max_connections": 16
                    }
                },
                "expected": {
                    "pool": {
                        "max_connections": 16
                    }
                }
            },
            {  # Full
                "original": {
                    "pool": {
                        "max_connections": 32,
                        "min_connections": 2
                    }
                },
                "expected": {
                    "pool": {
                        "max_connections": 32,
                        "min_connections": 2
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
    "oneOf": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'oneOf' with defaults",
            "type": "object",
            "unevaluatedProperties": False,
            "oneOf": [
                {
                    "additionalProperties": False,
                    "properties": {
                        "animal": {
                            "enum": ["dog", "cat"]
                        },
                        "name": {
                            "default": "Ralph"
                        },
                        "age": {
                            "minimum": 0
                        }
                    },
                    "required": ["animal"]
                },
                {
                    "additionalProperties": False,
                    "properties": {
                        "bicycle": {
                            "enum": ["road", "mountain", "gravel"]
                        },
                        "sprockets": {
                            "default": 9
                        }
                    },
                    "required": ["bicycle"]
                }
            ],
        },
        "instances": [  # Empty is not allowed!
            {  # First option, partial
                "original": {
                    "animal": "dog"
                },
                "expected": {
                    "animal": "dog",
                    "name": "Ralph"
                }
            },
            {  # First option, full
                "original": {
                    "animal": "cat",
                    "name": "Shadow",
                    "age": 7
                },
                "expected": {
                    "animal": "cat",
                    "name": "Shadow",
                    "age": 7
                }
            },
            {  # Second option, partial
                "original": {
                    "bicycle": "road"
                },
                "expected": {
                    "bicycle": "road",
                    "sprockets": 9
                }
            },
            {  # Second option, full
                "original": {
                    "bicycle": "gravel",
                    "sprockets": 12
                },
                "expected": {
                    "bicycle": "gravel",
                    "sprockets": 12
                }
            },
        ]
    },
    "anyOf": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'anyOf' with defaults",
            "type": "object",
            "anyOf": [
                {
                    "if": {"properties": {
                        "someInteger": {"multipleOf": 2}
                    }},
                    "then": {"properties": {
                        "message1": {"default": "Multiple of 2"}
                    }},
                },
                {
                    "if": {"properties": {
                        "someInteger": {"multipleOf": 3}
                    }},
                    "then": {"properties": {
                        "message2": {"default": "Multiple of 3"}
                    }},
                },
                {
                    "if": {"properties": {
                        "someInteger": {"multipleOf": 5}
                    }},
                    "then": {"properties": {
                        "message3": {"default": "Multiple of 5"}
                    }},
                },
            ]
        },
        "instances": [
            {  # None of
                "original": {
                    "someInteger": 7
                },
                "expected": {
                    "someInteger": 7
                }
            },
            {  # Some of
                "original": {
                    "someInteger": 6
                },
                "expected": {
                    "someInteger": 6,
                    "message1": "Multiple of 2",
                    "message2": "Multiple of 3"
                },
            },
            {  # All of
                "original": {
                    "someInteger": 30,
                    "message2": "Multiple of 3!!!!!!!",
                },
                "expected": {
                    "someInteger": 30,
                    "message1": "Multiple of 2",
                    "message2": "Multiple of 3!!!!!!!",
                    "message3": "Multiple of 5",
                },
            },
        ]
    },
    "dependentSchemas": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'dependentSchemas' with defaults",
            "type": "object",
            "properties": {
                "snack": {"type": "string"},
                "dessert": {"type": "string"}
            },
            "required": ["snack"],
            "dependentSchemas": {
                "dessert": {
                    "properties": {
                        "utensil": {"enum": ["Spoon", "Fork"], "default": "Fork"},
                        "coffee": {"type": "string"}
                    },
                    "dependentSchemas": {
                        "coffee": {
                            "properties": {
                                "mint": {"type": "boolean", "default": True},
                            },
                        }
                    }
                }
            }
        },
        "instances": [
            {  # Empty
                "original": {
                    "snack": "Popcorn"
                },
                "expected": {
                    "snack": "Popcorn"
                }
            },
            {  # Partial
                "original": {
                    "snack": "Popcorn",
                    "coffee": "Americano"
                },
                "expected": {
                    "snack": "Popcorn",
                    "coffee": "Americano"
                }
            },
            {  # Partial
                "original": {
                    "snack": "Popcorn",
                    "dessert": "Cake"
                },
                "expected": {
                    "snack": "Popcorn",
                    "dessert": "Cake",
                    "utensil": "Fork"
                },
            },
            {  # Partial
                "original": {
                    "snack": "Popcorn",
                    "dessert": "Ice Cream",
                    "utensil": "Spoon",
                    "coffee": "Espresso"
                },
                "expected": {
                    "snack": "Popcorn",
                    "dessert": "Ice Cream",
                    "utensil": "Spoon",
                    "coffee": "Espresso",
                    "mint": True
                },
            },
            {  # Full
                "original": {
                    "snack": "Popcorn",
                    "dessert": "Ice Cream",
                    "utensil": "Spoon",
                    "coffee": "Flat White",
                    "mint": False
                },
                "expected": {
                    "snack": "Popcorn",
                    "dessert": "Ice Cream",
                    "utensil": "Spoon",
                    "coffee": "Flat White",
                    "mint": False
                },
            },
        ]
    },
    "items": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'items' with defaults",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "preference": {
                        "enum": ["vegan", "vegetarian", "none"],
                        "default": "vegan"
                    },
                    "baggage": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "bag": {"type": "string"},
                                "checked": {"type": "boolean", "default": False}
                            }
                        }
                    },
                    "favorite_numbers": {
                        "type": "array",
                        "items": {"type": "integer"}
                    }
                },
                "required": ["name"]
            }
        },
        "instances": [
            {  # Mixed full
                "original": [
                    {
                        "name": "Charlie",
                    },
                    {
                        "name": "Kelly",
                        "favorite_numbers": [0, 1, 1, 2, 3, 5, 8, 13]
                    },
                    {
                        "name": "Laura",
                        "preference": "vegetarian"
                    },
                    {
                        "name": "John",
                        "baggage": [
                            {"bag": "backpack"},
                            {"bag": "suitcase", "checked": True}
                        ]
                    }
                ],
                "expected": [
                    {
                        "name": "Charlie",
                        "preference": "vegan"
                    },
                    {
                        "name": "Kelly",
                        "favorite_numbers": [0, 1, 1, 2, 3, 5, 8, 13],
                        "preference": "vegan"
                    },
                    {
                        "name": "Laura",
                        "preference": "vegetarian"
                    },
                    {
                        "name": "John",
                        "preference": "vegan",
                        "baggage": [
                            {"bag": "backpack", "checked": False},
                            {"bag": "suitcase", "checked": True}
                        ]
                    }
                ],
            }
        ]
    },
    "prefixItemsAndItems": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'prefixItems' and 'items' with defaults",
            "type": "array",
            "prefixItems": [
                {"type": "number"},
                {"type": "string"},
                {"enum": ["Street", "Avenue", "Drive"], "default": "Drive"}
            ],
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer", "default": 11}
                },
                "required": ["name"]
            }
        },
        "instances": [
            {   # Missing prefixItems are only filled if there are only
                # default-resolving prefixItem schemas remaining.
                "original": [4],
                "expected": [4]
            },
            {  # Only default-resolving prefixes remaining, so they are filled.
                "original": [4, "Privet"],
                "expected": [4, "Privet", "Drive"]
            },
            {  # All prefixItems with incomplete items
                "original": [4, "Privet", "Drive", {"name": "Harry"}, {"name": "Dudley", "age": 10}],
                "expected": [4, "Privet", "Drive", {"name": "Harry", "age": 11}, {"name": "Dudley", "age": 10}]
            },
            {  # Only prefixItems
                "original": [1428, "Elm", "Street"],
                "expected": [1428, "Elm", "Street"]
            },
        ]
    },
    "prefixItems": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'prefixItems' with defaults",
            "type": "array",
            "prefixItems": [
                {"type": "string"},
                {
                    "properties": {
                        "carry-on": {"type": "string"},
                        "size": {"type": "array", "default": [0.5, 0.4, 0.3]}
                    }
                },
                {
                    "properties": {
                        "personal-bag": {"type": "string"},
                        "weight": {"type": "integer", "default": 9}
                    }
                },
            ]
        },
        "instances": [
            {   # prefixItems are filled
                "original": [
                    "John",
                    {"carry-on": "duffel"},
                    {"personal-bag": "purse", "weight": 2}
                ],
                "expected": [
                    "John",
                    {"carry-on": "duffel", "size": [0.5, 0.4, 0.3]},
                    {"personal-bag": "purse", "weight": 2}
                ]
            },
            {   # Missing prefixItems are only filled if there are only
                # default-resolving prefixItem schemas remaining.
                "original": [],
                "expected": []
            },
            {   # Default-resolving prefixItems will fill if all remaining
                # prefixItems are default-resolving!
                "original": [
                    "John"
                ],
                "expected": [
                    "John",
                    {"size": [0.5, 0.4, 0.3]},
                    {"weight": 9}
                ]
            }
        ]
    },
    "conflictingDefaultBad": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'dependentSchemas' with conflicting defaults",
            "type": "object",
            "properties": {
                "claim": {"type": "string"},
                "claim_exists": {"type": "boolean", "default": False}
            },
            "dependentSchemas": {
                "claim": {
                    "properties": {
                        "claim_exists": {"default": True}
                    }
                }
            }
        },
        "instances": [
            {  # Empty
                "original": {
                },
                "expected": {
                    "claim_exists": False
                }
            },
            {  # Partial
                "original": {
                    "claim": "Sky is blue"
                },
                "expected": {
                    "claim": "Sky is blue",
                    "claim_exists": False
                }
            }
        ]
    },
    "conflictingDefaultGood": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'dependentSchemas' with conflicting defaults",
            "type": "object",
            "dependentSchemas": {
                "claim": {
                    "properties": {
                        "claim_exists": {"default": True}
                    }
                }
            },
            "properties": {
                "claim": {"type": "string"},
                "claim_exists": {"type": "boolean", "default": False}
            }
        },
        "instances": [
            {  # Empty
                "original": {
                },
                "expected": {
                    "claim_exists": False
                }
            },
            {  # Partial
                "original": {
                    "claim": "Sky is blue"
                },
                "expected": {
                    "claim": "Sky is blue",
                    "claim_exists": True
                }
            }
        ]
    },
    "nestedKeywords": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'dependentSchemas' with nested keywords",
            "type": "object",
            "properties": {
                "subObject": {
                    "allOf": [
                        {
                            "properties": {
                                "subString": {"default": "nested"}
                            }
                        }
                    ]
                }
            }
        },
        "instances": [
            {  # Empty
                "original": {
                },
                "expected": {
                    "subObject": {"subString": "nested"}
                }
            },
            {  # Full
                "original": {
                    "subObject": {"subString": "already taken"}
                },
                "expected": {
                    "subObject": {"subString": "already taken"}
                }
            }
        ]
    },
    "emptyExisting": {
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "JSON Schema of 'dependentSchemas' with nested keywords",
            "type": "object",
            "properties": {
                "subObject": {
                    "allOf": [
                        {
                            "if": {"required": ["exists"]},
                            "then": {
                                "properties": {
                                    "string": {"default": "nested"}
                                }
                            }
                        }
                    ]
                }
            }
        },
        "instances": [
            {  # Empty
                "original": {
                    "subObject": {}
                },
                "expected": {
                    "subObject": {}
                }
            },
            {  # Partial
                "original": {
                    "subObject": {"exists": True}
                },
                "expected": {
                    "subObject": {"exists": True, "string": "nested"}
                }
            },
            {  # Partial
                "original": {
                    "subObject": {"string": "hello"}
                },
                "expected": {
                    "subObject": {"string": "hello"}
                }
            }
        ]
    }
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
@ pytest.mark.parametrize(
    "schema",
    schemas
)
def test_schema_is_valid_meta_schema(schema):
    assert protocols.Validator.check_schema(schema) is None


# All instances must be valid to their schema
@ pytest.mark.parametrize(
    "instance, schema",
    instance_schema_pairs
)
def test_instance_is_valid_schema(instance, schema):
    assert validate(instance, schema) is None


# All filled instances must equal their expected
@ pytest.mark.parametrize(
    "original, schema, expected",
    original_schema_expected_triplets
)
def test_filled_instance_is_equal_to_expected(original, schema, expected):
    fill_default(original, schema)
    assert original == expected
