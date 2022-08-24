"""Tests for the checks module."""

from aga.checks import with_captured_stdout


def test_with_captured_stdout() -> None:
    """Test `with_captured_stdout`."""

    def under_test(x: int) -> int:
        """Square x and print -x."""
        print(-x)
        return x * x

    assert with_captured_stdout(under_test)(5) == ("-5\n", 25)
