"""Utilities for configuring `aga`."""

from dataclasses import dataclass, field, fields

import toml
from dacite import from_dict  # type: ignore


@dataclass
class AgaUiConfig:
    """Aga's UI-related configuration."""

    test_name_fmt: str = "Test on {args}{kwargs}."

    def update_weak(self, other: "AgaUiConfig") -> None:
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

    ui: AgaUiConfig = field(default_factory=AgaUiConfig)

    def update_weak(self, other: "AgaConfig") -> None:
        """Update all default attributes of self to match other."""
        self.ui.update_weak(other.ui)


def load_config_from_path(path: str) -> AgaConfig:
    """Load the toml file at path."""
    return from_dict(  # type: ignore
        data_class=AgaConfig,
        data=toml.load(path),
    )
