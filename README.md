[![Master Build Status](https://travis-ci.org/d0c-s4vage/pfp.svg?branch=master)](https://travis-ci.org/d0c-s4vage/pfp)
[![PyPI Statistics](https://img.shields.io/pypi/dm/pfp)](https://pypistats.org/packages/pfp)
[![Latest Release](https://img.shields.io/pypi/v/pfp)](https://pypi.python.org/pypi/pfp/)
[![Documentation Status](https://readthedocs.org/projects/pfp/badge/?version=latest)](https://pfp.readthedocs.io/en/latest/)

# pfp

`pfp` is a python-based interpreter for 010 template scripts.

See the main documentation on [Read the Docs](http://pfp.readthedocs.org/en/latest/)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## Installation

Install pfp with

	pip install --upgrade pfp

## Tl;DR

You don't feel like going to read the docs? This should get you
started parsing something using 010 templates:

```python
import pfp

dom = pfp.parse(
	data_file="~/Desktop/image.png",
	template_file="~/Desktop/PNGTemplate.bt"
)
```
