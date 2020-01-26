[![Master Build Status](https://travis-ci.org/d0c-s4vage/pfp.svg?branch=master)](https://travis-ci.org/d0c-s4vage/pfp)
[![PyPI Statistics](https://img.shields.io/pypi/dm/pfp)](https://pypistats.org/packages/pfp)
[![Latest Release](https://img.shields.io/pypi/v/pfp)](https://pypi.python.org/pypi/pfp/)
[![Documentation Status](https://readthedocs.org/projects/pfp/badge/?version=latest)](https://pfp.readthedocs.io/en/latest/)
[![Coverage Status](https://coveralls.io/repos/github/d0c-s4vage/pfp/badge.svg?branch=master)](https://coveralls.io/github/d0c-s4vage/pfp?branch=master)

[![Twitter Follow](https://img.shields.io/twitter/follow/d0c_s4vage?style=plastic)](https://twitter.com/d0c_s4vage)

# pfp

`pfp` is a python-based interpreter for 010 template scripts.

See the main documentation on [Read the Docs](http://pfp.readthedocs.org/en/latest/)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## Installation

Install pfp with

	pip install --upgrade pfp

## Tl;DR

### CLI

```bash
pfp -t path/to/template input_file
```

All available options for the pfp CLI:

```
usage: pfp [-h] -t TEMPLATE [--show-offsets] [-k] input

Run pfp on input data using a specified 010 Editor template for parsing

positional arguments:
  input                 The input data stream or file to parse. Use '-' for
                        piped data

optional arguments:
  -h, --help            show this help message and exit
  -t TEMPLATE, --template TEMPLATE
                        The template to parse with
  --show-offsets        Show offsets in the parsed data of parsed fields
  -k, --keep            Keep successfully parsed data on error
```

### Python Library

This should get you started parsing something using 010 templates:

```python
import pfp

dom = pfp.parse(
	data_file="~/Desktop/image.png",
	template_file="~/Desktop/PNGTemplate.bt"
)
```
