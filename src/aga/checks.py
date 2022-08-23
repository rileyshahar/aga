"""Additional checks and filters for problems."""

from io import StringIO
from typing import Any, Callable
from unittest.mock import patch


def with_captured_stdout(func: Callable[..., Any]) -> Callable[..., tuple[str, Any]]:
    """Run func, returning its stdout and normal return value."""

    def inner(*args: Any, **kwargs: Any) -> tuple[str, Any]:
        with patch("sys.stdout", new=StringIO()) as stdout:
            func_out = func(*args, **kwargs)

        return stdout.getvalue(), func_out

    return inner
