"""Utilities for configuring `aga`."""

from dataclasses import dataclass, field, fields
from importlib.resources import files

import toml
from dacite import from_dict  # type: ignore


@dataclass
class AgaTestConfig:
    """Aga's test-related configuration."""

    name_sep: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.name_sep)
    name_fmt: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.name_fmt)
    failure_msg: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.failure_msg)
    error_msg: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.error_msg)

    def update_weak(self, other: "AgaTestConfig") -> None:
        """Update all default attributes of self to match other."""
        # iterate over all the fields of the dataclass, checking them against the
        # default value, and updating them to the other value if they match the default
        # value
        for attr in fields(self):
            if attr.default_factory() == getattr(self, attr.name):  # type: ignore
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


_DEFAULT_CONFIG: AgaConfig = load_config_from_path(
    # this is type safe, but there's not actually a safe way to indicate that to mypy,
    # since `Traversable` (the type returned by `joinpath`) isn't re-exported by
    # `importlib.resources`
    files("aga").joinpath("defaults.toml")  # type: ignore
)
