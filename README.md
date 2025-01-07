# jsonschema_fill_default
Fill a JSON instance with the defaults of the JSON Schema it is valid against

## Developers

### Set up development environment with `conda` and `poetry`

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

#### Using `__init__.py` to declare a 'public' API for the module

_From [this post](https://www.reddit.com/r/Python/comments/1bbbwk/comment/c95cjs5/) by reostra:_

For example, having

```
stuff/
  __init__.py
  bigstuff.py
    Stuffinator()
    Stuffinatrix()
  privateStuff.py
```

where __init__.py contains

```
from .bigstuff import Stuffinator, Stuffinatrix
```

and thereby users can import those with

```
from stuff import Stuffinator, Stuffinatrix
```

which essentially says that stuff.Stuffinator and stuff.Stuffinatrix are the only parts of the module intended for public use.
While there's nothing stopping people from doing an 'import stuff.bigstuff.Stuffometer' or 'import stuff.privateStuff.HiddenStuff', they'll at least know they're peeking behind the curtain at that point.
Rather than being implicit, I find it's rather explicit.
