"""Environment value wrapper."""
from __future__ import annotations

import types
from typing import Iterable, Any


class Environment(dict[str, Any]):
    """Environment value wrapper."""

    def __init__(self, env_targets: Iterable[str]) -> None:
        super().__init__()
        for target in env_targets:
            self[target] = None

    def update_from_module(self, mod: types.ModuleType) -> None:
        """Update environment values from a given module."""
        for value_name in self.keys():
            if value_name not in vars(mod):
                raise ValueError(
                    f"The variable `{value_name} does not exist in the module {mod}"
                )
            self[value_name] = getattr(mod, value_name)

    def __getattr__(self, item: str) -> Any:
        """Get the value of an environment variable."""
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(e) from e
