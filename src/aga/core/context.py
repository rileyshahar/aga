"""Environment value wrapper."""
from __future__ import annotations

from typing import Iterable, Any


class SubmissionContext(dict[str, Any]):
    """Environment value wrapper."""

    def __init__(self, env_targets: Iterable[str]) -> None:
        super().__init__()
        for target in env_targets:
            self[target] = None

    def update_from_path(self, path: str) -> None:
        """Update environment values from a given module."""
        from ..loader import load_symbol_from_path

        for symbol in self.keys():
            self[symbol] = load_symbol_from_path(path, symbol)

    def __getattr__(self, item: str) -> Any:
        """Get the value of an environment variable."""
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(e) from e
