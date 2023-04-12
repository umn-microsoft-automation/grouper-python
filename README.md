# grouper-python

## Installation

To install grouper library only:

``` sh
pip install .
```

To install additional requirements for running the included scripts:

``` sh
pip install .[script]
```

To install for development:

``` sh
pip install --editable .[dev]
```

This will install so the `grouper` module is based off the source code,
and also installs neccessary linters and testing requirements.
Currently there are no "tests" written for this code,
but at the very least it passes `pylama` and `mypy`.

## Script usage

To use the included scripts (`docs_base.py` and `docs_site.py`)
you will need to setup a `.env` file.
Copy `.env.template` to `.env`.
Change the values for GROUPER_USER, GROUPER_PWD, and if neccessary, GROUPER_BASE_URL.
If there are double quotes (`"`) in your password, surround it with single quotes (`'`)
instead of the double quotes in the sample file.

### Specifying sites

Specify the sites to create groups for using a text file (by default, `sites.txt`)
in the root of this repository.
Specify the URLs, one per line.
This file will be read by `docs_site.py`.
