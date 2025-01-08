from typing import Union

from jsonschema import validate, ValidationError


def fill_default(instance: Union[dict, list], schema: dict) -> Union[dict, list]:
    """Fill a JSON instance with schema defaults

    Recursively fills a JSON instance with the defaults of a schema with
    keywords:
    - "properties",
    - "if-then(-else)",
    - "allOf",
    - "anyOf",
    - "oneOf",
    - "dependentSchemas",
    - "items", and
    - "prefixItems".

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict, list): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12

    Returns:
        instance (dict, list): Mutated filled instance (not a copy).
    """
    for keyword in schema:  # Apply keywords in order for predictable defaults
        if keyword == "properties":
            _fill_properties(instance, schema)
        if keyword == "allOf":
            _fill_allof(instance, schema)
        if keyword == "anyOf":
            _fill_anyof(instance, schema)
        if keyword == "if":
            _fill_ifthenelse(instance, schema)
        if keyword == "oneOf":
            _fill_oneof(instance, schema)
        if keyword == "dependentSchemas":
            _fill_dependentschemas(instance, schema)
    if isinstance(instance, list):  # Handle "(prefix)Items" for lists (arrays)
        # Get quantities
        n_instance = len(instance)
        n_schema_prefixitems = 0
        n_schema_non_default_prefixitems = 0
        if "prefixItems" in schema:
            n_schema_prefixitems = len(schema["prefixItems"])

            # Find number of non-continuously-default prefixItems by looping
            # in reverse until default is not found in that prefixItem.
            n_schema_non_default_prefixitems = n_schema_prefixitems
            for prefixitem in reversed(schema["prefixItems"]):
                if "default" in prefixitem:
                    n_schema_non_default_prefixitems -= 1
                else:
                    break
        n_instance_items = n_instance - n_schema_prefixitems
        if n_instance_items > 0:
            if "items" in schema:
                _fill_items(instance[-n_instance_items:], schema)
        elif n_instance >= n_schema_non_default_prefixitems:
            print(instance[n_schema_non_default_prefixitems:n_schema_prefixitems])
    return None


def _fill_properties(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "properties" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Adapted from https://stackoverflow.com/a/76686673/20921535 by Tom-tbt.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "properties" keyword

    Returns:
        None
    """
    for _property, subschema in schema["properties"].items():
        if "properties" in subschema:  # Recursion
            if _property not in instance:
                instance[_property] = dict()
            fill_default(instance[_property], subschema)
            if len(instance[_property]) == 0:  # No default found inside
                del instance[_property]
        if _property not in instance \
                and "default" in subschema:
            instance[_property] = subschema["default"]
        # Fill missing keys if instance already exists as object
        elif _property in instance \
                and "default" in subschema \
                and isinstance(instance[_property], dict):
            for default_key in subschema["default"]:
                if default_key not in instance[_property]:
                    instance[_property][default_key] = \
                        subschema["default"][default_key]
        if any(key in ["oneOf", "allOf", "anyOf", "if", "dependentSchemas"] for key in subschema):
            fill_default(instance[_property], subschema)
        if "items" in subschema:
            if _property in instance:  # Instance must have array to fill
                fill_default(instance[_property], subschema)
    return None


def _fill_oneof(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "oneOf" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "oneOf" keyword

    Returns:
        None
    """
    i = 0
    n = len(schema["oneOf"])
    while i < n:  # Iterate subschemas until the instance is valid to it
        subschema = schema["oneOf"][i]
        try:
            validate(instance, subschema)
        except ValidationError:  # If not valid, go to next subschema
            i += 1
        else:  # If valid, fill with that subschema
            fill_default(instance, subschema)
            return None
    return None


def _fill_allof(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "allOf" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "allOf" keyword

    Returns:
        None
    """
    for subschema in schema["allOf"]:  # Instance is valid to all, so fill all
        fill_default(instance, subschema)
    return None


def _fill_anyof(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "anyOf" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "anyOf" keyword

    Returns:
        None
    """
    # Fill instance with defaults of all subschemas it is valid to
    for subschema in schema["anyOf"]:
        try:
            validate(instance, subschema)
        except ValidationError:
            continue  # Skip to next subschema if instance is not valid to it
        else:
            fill_default(instance, subschema)
    return None


def _fill_dependentschemas(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "dependentSchemas" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "dependentSchemas" keyword

    Returns:
        None
    """
    for _property, subschema in schema["dependentSchemas"].items():
        if _property in instance:
            fill_default(instance, subschema)
    return None


def _fill_items(instance: list, schema: dict):
    """Recursively fill a list of items with schema "items" defaults

    Fills all nested structures.

    Mutates the instance input items, so None is returned.

    Args:
        instance (array): List of items valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "items" keyword

    Returns:
        None
    """
    for item in instance:
        fill_default(item, schema["items"])
    return None


def _fill_ifthenelse(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "if-then(-else)" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "if", "then", and (optionally) "else" keyword

    Returns:
        None
    """
    try:
        validate(instance, schema["if"])
    except ValidationError:  # If invalid, fill instance with else if it exists
        if "else" in schema:
            fill_default(instance, schema["else"])
    else:
        fill_default(instance, schema["then"])
    return None
