# grouper-python

This is a module to interact with the [Grouper Web Services API](https://spaces.at.internet2.edu/display/Grouper/Grouper+Web+Services).

## Basic Usage

Operations will start by creating a `GrouperClient` object.

``` python
from grouper_python import GrouperClient

grouper_client = GrouperClient(base_url, username, password)
```

`GrouperClient` can also be used as a context manager.

``` python
from grouper_python import GrouperClient

with GrouperClient(base_url, username, password) as grouper_client:
    ...
```

The `base_url` should end in something like
`grouper-ws/servicesRest/v2_6_000`.

With a `GrouperClient` object, you can query for a subject, stem, or group.
You can also "search" for groups or subjects.

Once you have an object, you can perform various operations against it.
To create a new group or stem for example, you would get the "parent" stem,
and then use `create_child_stem()` or `create_child_group()` to create that
stem or group in that parent.

## Installation

To install grouper library only:

``` sh
pip install .
```

To install for development:

``` sh
pip install --editable .[dev]
```

This will install so the `grouper` module is based off the source code,
and also installs neccessary linters and testing requirements.
