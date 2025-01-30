# jsonschema-fill-default

Fill a JSON instance in Python with the missing defaults from its [JSON Schema](https://json-schema.org/) [Draft 2020-12](https://json-schema.org/draft/2020-12)-valid schema.

```python
from jsonschema_fill_default import fill_default

schema = {
    "properties": {
        "text": {"default": "Hello"},
        "font": {"default": 12},
    }
}

instance = {"text": "Goodbye"}

fill_default(instance, schema)  # Mutates instance!
```
```python
>>> instance
    {
        "text": "Goodbye",
        "font": 12
    }
```

> [!CAUTION]
> Filled instances are not automatically validated.
>
> See [Load, validate, deference, fill](#load-validate-dereference-fill) for how you can validate instances and schemas.


## Install

`jsonschema-fill-default` is available on [`PyPI`](https://pypi.org/project/jsonschema-fill-default/). You can install using [`pip`](https://pip.pypa.io/en/stable/):

```command
pip install jsonschema-fill-default
```

## Features

- Fills all missing defaults, including nested ones.

- Uses the first applicable default if multiple defaults exist for a single property.

- Works with the following keywords and any combination thereof (see [examples](#examples) for details):
  - `"properties"`
  - `"allOf"`
  - `"anyOf"`
  - `"oneOf"`
  - `"dependentSchemas"`
  - `"if-then(-else)"`
  - `"prefixItems"`
  - `"items"`

> [!IMPORTANT]
> - The instance must already be valid to its schema.
> - The schema itself must be a valid [Draft 2020-12](https://json-schema.org/draft/2020-12) [JSON Schema](https://json-schema.org/).
> - The filled instance is **not automatically validated**.


## Examples


### Load, validate, dereference, fill

See unabridged script at [examples/load_validate_dereference_fill.py](https://github.com/larsmaxfield/jsonschema-fill-default/blob/main/examples/load_validate_dereference_fill.py).

```python
import json

from jsonschema import validate, protocols
from jsonref import replace_refs
from jsonschema_fill_default import fill_default


schema_filename = "bicycle.schema.json"
instance = {
    "style": "road",
    "color": "purple",
    "tire": {
        "width": 28
    }
}

with open(schema_filename, 'r') as file:
    schema = json.load(file)

protocols.Validator.check_schema(schema)  # Validate schema
validate(instance, schema)  # Validate instance against schema

schema = replace_refs(schema) # De-reference schema "$refs"

fill_default(instance, schema)  # Fill instance (mutates)

validate(instance, schema)  # Validate filled instance

print(f"\nFilled:\n{json.dumps(instance, indent=4)}")
```

### Nested defaults

```python
from jsonschema_fill_default import fill_default

schema = {
    "properties": {
        "someString": {"default": "The default string"},
        "someObject": {
            "properties": {
                "someNumber": {"default": 3.14},
                "someBoolean": {"default": True}}}}}

instance = {
    "someObject": {
        "someNumber": -1
    }
}

fill_default(instance, schema)
```
```python
original
    {
        "someObject": {
            "someNumber": -1
        }
    }

filled
    {
        "someString": "The default string",
        "someObject": {
            "someNumber": -1,
            "someBoolean": True
        }
    }
```


### Conditional properties with defaults with `"dependentSchemas"`

```python
from jsonschema_fill_default import fill_default

schema = {
    "properties": {"some_number": {"default": 100}},
    "dependentSchemas": {
        "some_bool": {
            "properties": {
              "some_string": {"default": "some_bool given"}}}}}

without_bool = {}
with_bool = {"some_bool": False}

fill_default(without_bool, schema)`
fill_default(with_bool, schema)
```
```python
original  {}
filled    {"some_number": 100}

original
    {
        "some_bool": False
    }
filled
    {
        "some_number": 100,
        "some_bool": False,
        "some_string": "some_bool given"
    }
```


### Conditional defaults with `"if-then-else"`

```python
from jsonschema_fill_default import fill_default

schema = {
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
        "conditionalString": {"default": "someInteger not given"}
    }}
}

none = {}
odd = {"someInteger": 3}
even = {"someInteger": 4}

fill_default(none, schema)
fill_default(odd, schema)
fill_default(even, schema)
```
```python
original  {}
filled    {"conditionalString": "someInteger not given"}

original  {"someInteger": 3}
filled    {"someInteger": 3, "conditionalString": "Odd integer"}

original  {"someInteger": 4}
filled    {"someInteger": 4, "conditionalString": "Even integer"}
```

### Different properties and defaults with `"oneOf"`

```python
from jsonschema_fill_default import fill_default

schema = {
    "unevaluatedProperties": False,
    "oneOf": [
        {
            "additionalProperties": False,
            "properties": {
                "food": {"enum": ["cake", "taco"]},
                "price": {"default": 9.95}
            },
            "required": ["food"]
        },
        {
            "additionalProperties": False,
            "properties": {
                "activity": {
                    "enum": ["walk", "talk", "eat"]
                },
                "duration": {
                    "default": 30
                }
            },
            "required": ["activity"]
        }
    ],
}

A = {"food": "cake"}
B = {"activity": "eat"}

fill_default(A, schema)
fill_default(B, schema)
```
```python
original  {"food": "cake"}
filled    {"food": "cake", "price": 9.95}


original  {"activity": "eat"}
filled    {"activity": "eat", "duration": 30}
```

### Fill array defaults with `"prefixItems"` and `"items"`

```python
from jsonschema_fill_default import fill_default

schema = {
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
}

a = [4, "Privet"]
fill_default(a, schema)
```
```python
# Missing prefixItems are only filled if there are only default-resolving prefixItem schemas remaining.

original  [4]
filled    [4]

original  [4, "Privet"]
filled    [4, "Privet", "Drive"]


# Existing prefixItems and items are filled

original  [4, "Privet", "Drive",
           {"name": "Harry"},
           {"name": "Dudley"}]
filled    [4, "Privet", "Drive",
           {"name": "Harry", "age": 11},
           {"name": "Dudley", "age": 11}]


original  [1428, "Elm", "Street"]
filled    [1428, "Elm", "Street"]
```

## Developers

### Development environment with `conda` and `poetry`

I use `conda` to create a virtual environment with Python, `pip`, and `poetry`.

I then add the dependencies using `poetry install`, which automatically adds them to that `conda` environment.

Here's how:

#### 1. Clone the repo

#### 2. Create and activate a virtual environment using `conda`

For example, create and activate a virtual environment `env` in the root of the project repo using `requirements.dev.txt` as reference:

```
cd /root/of/this/repo
conda env create --prefix ./env python=3.9
conda activate ./env
pip install poetry==1.8.5
```

I don't use an `environment.yml` to solve and install the `conda` environment because it's typically slower than just running the above "manual" install.

#### 3. Install `poetry` dependencies

```
poetry install
```

#### 4. Use

Once set up, you can use the development environment in the future by simply activating the `conda` environment.

If you used the example above, that would be:

```
cd /root/of/this/repo
conda activate ./env
```

### How to release

1. Checkout branch 
2. Update version X.Y.Z.YYYYMMDD in `pyproject.toml`
    - Bump X.Y.Z according to semantic versioning 2.0.0
    - Set YYYYMMDD according to current UTC date
4. Update `poetry.lock` with `poetry update`
5. Push changes
6. Merge with main
7. Create release with title and tag `vX.Y.Z.YYYYMMDD` (prepend `v` in both)
8. PyPI is automatically published


### Paradigms

#### Use the top-level `__init__.py` to declare a 'public' API for the module

_From [this post](https://www.reddit.com/r/Python/comments/1bbbwk/comment/c95cjs5/) by reostra:_

> For example, having
> 
> ```
> stuff/
>   __init__.py
>   bigstuff.py
>     Stuffinator()
>     Stuffinatrix()
>   privateStuff.py
> ```
> 
> where **init**.py contains
> 
> ```
> from .bigstuff import Stuffinator, Stuffinatrix
> ```
> 
> and thereby users can import those with
> 
> ```
> from stuff import Stuffinator, Stuffinatrix
> ```
> 
> which essentially says that stuff.Stuffinator and stuff.Stuffinatrix are the only parts of the module intended for public use.
> 
> While there's nothing stopping people from doing an 'import stuff.bigstuff.Stuffometer' or 'import stuff.privateStuff.HiddenStuff', they'll at least know they're peeking behind the curtain at that point.
> 
> Rather than being implicit, I find it's rather explicit.
> 


## Credits

jsonschema-fill-default is by Lars Maxfield

Recursive filling of `"properties"` based on [Tom-tbt](https://stackoverflow.com/users/10712860/tom-tbt)'s answer to [Set default values according to JSON schema automatically](https://stackoverflow.com/questions/72044825/set-default-values-according-to-json-schema-automatically) on Stack Overflow.
