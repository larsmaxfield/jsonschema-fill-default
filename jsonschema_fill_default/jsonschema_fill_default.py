from jsonschema import validate, ValidationError


def fill_default(instance: dict, schema: dict):
    """Fill a JSON instance with schema defaults

    Recursively fills a JSON instance with the defaults of a schema with
    keywords "properties", "if-then(-else)", "allOf", "anyOf", and "oneOf".

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to draft 2020-12

    Returns:
        instance (dict): Mutated filled instance (not a copy).
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
    return None


def _fill_properties(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "properties" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Adapted from https://stackoverflow.com/a/76686673/20921535 by Tom-tbt.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to draft 2020-12 with a top-level
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
        if any(key in ["oneOf", "allOf", "anyOf", "if"] for key in subschema):
            fill_default(instance[_property], subschema)
    return None


def _fill_oneof(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "oneOf" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to draft 2020-12 with a top-level
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
        schema (dict): JSON schema adhering to draft 2020-12 with a top-level
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
        schema (dict): JSON schema adhering to draft 2020-12 with a top-level
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


def _fill_ifthenelse(instance: dict, schema: dict):
    """Recursively fill a JSON instance with schema "if-then(-else)" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to draft 2020-12 with a top-level
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
