"""Utilities for configuring `aga`."""

from dataclasses import dataclass, field, fields

import toml
from dacite import from_dict  # type: ignore


@dataclass
class AgaTestConfig:
    """Aga's test-related configuration."""

    name_sep: str = ","
    name_fmt: str = "Test on {args}{sep}{kwargs}."
    failure_msg: str = (
        "Your submission didn't give the output we expected. "
        "We checked it with {input} and got {output}, but we expected {expected}."
    )

    error_msg: str = (
        "A python {type} occured while running your submission: "
        "{message}.\n\nHere's what was running when it happened:{traceback}."
    )

    def update_weak(self, other: "AgaTestConfig") -> None:
        """Update all default attributes of self to match other."""
        # iterate over all the fields of the dataclass, checking them against the
        # default value, and updating them to the other value if they match the default
        # value
        for attr in fields(self):
            if attr.default == getattr(self, attr.name):
                setattr(self, attr.name, getattr(other, attr.name))


@dataclass
class AgaConfig:
    """Aga's configuration."""

    test: AgaTestConfig = field(default_factory=AgaTestConfig)

    def update_weak(self, other: "AgaConfig") -> None:
        """Update all default attributes of self to match other."""
        self.test.update_weak(other.test)


def load_config_from_path(path: str) -> AgaConfig:
    """Load the toml file at path."""
    return from_dict(  # type: ignore
        data_class=AgaConfig,
        data=toml.load(path),
    )
