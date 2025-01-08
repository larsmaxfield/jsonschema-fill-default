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

See [examples](#examples) for showcasing of these features:

- Fills all missing defaults, including nested ones.

- Works with the following keywords and any combination thereof:
  - `"properties"`
  - `"allOf"`
  - `"anyOf"`
  - `"oneOf"`
  - `"dependentSchemas"`
  - `"if-then(-else)"`
  - `"prefixItems"`
  - `"items"`

- Uses the first applicable default if multiple defaults exist for a single property.

- Helps you verify a schema's defaults.

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
                "someBoolean": {"default": True}
            }
        }
    },
}

instance = {
    "someObject": {
        "someNumber": -1
    }
}

fill_default(instance, schema)
```
```python
>>> instance

{
    "someString": "The default string",
    "someObject": {
        "someNumber": -1,
        "someBoolean": True
    }
}
```


### Conditional properties with defaults with `"if-then"`

```python
from jsonschema_fill_default import fill_default

schema = {
    "properties": {"someNumber": {"default": 100}},
    "if": {
        "required": ["someBoolean"]
    },
    "then": {"properties": {
        "conditionalString": {"default": "someBoolean was given"}
    }}
}

without_bool = {}
with_bool = {"someBoolean": True}

fill_default(without_bool, schema)
fill_default(with_bool, schema)
```
```python
>>> without_bool

{
    "someNumber": 100
}

>>> with_bool

{
    "someNumber": 100,
    "someBoolean": True,
    "conditionalString": "someBoolean was given"
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
        "conditionalString": {"default": "No integer given"}
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
>>> none

{
    "conditionalString": "No integer given"
}

>>> odd

{
    "someInteger": 3,
    "conditionalString": "Odd integer"
}

>>> even

{
    "someInteger": 4,
    "conditionalString": "Even integer"
}
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
>>> A

{
    "food": "cake",
    "price": 9.95
}

>>> B

{
    "activity": "eat",
    "duration": 30
}
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
