"""Install the library for usage on gradescope.

This is _not_ a permanent solution, it's just a hack so we don't need to continually
push to PyPI while developing. (Even Test PyPI doesn't really work, it's not designed
for this sort of thing and you don't want to have to push to test local changes.) We
should either:

1. Find a way to automatically generate `setup.py`, maybe poetry has an API for this but
I couldn't find anything.
2. Find a better way to install the package from in gradescope without needing to fetch
it from PyPI.
"""

from setuptools import setup  # type: ignore

setup(
    name="aga",
    version="0.10.0",
    install_requires=[
        "dataclasses-json >= 0.5.6",
        "dill >= 0.3.4",
        "gradescope-utils >= 0.4.0",
        "typer >= 0.4.0",
        "dacite >= ^1.6.0",
        "toml >= ^0.10.2",
        "types-toml >= ^0.10.8",
    ],
)
