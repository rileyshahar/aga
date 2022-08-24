"""Additional checks and filters for problems."""

from io import StringIO
from typing import Any, Callable, TypeVar
from unittest.mock import patch

Output = TypeVar("Output")


def with_captured_stdout(
    func: Callable[..., Output]
) -> Callable[..., tuple[str, Output]]:
    """Run func, returning its stdout and normal return value."""

    def inner(*args: Any, **kwargs: Any) -> tuple[str, Any]:
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            func_out = func(*args, **kwargs)

        return stdout.getvalue(), func_out

    return inner
