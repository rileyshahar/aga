"""Tests for the checks module."""

import ast

from aga.checks import Disallow, with_captured_stdout


def test_with_captured_stdout() -> None:
    """Test `with_captured_stdout`."""

    def under_test(x: int) -> int:
        """Square x and print -x."""
        print(-x)
        return x * x

    assert with_captured_stdout(under_test)(5) == ("-5\n", 25)


def test_disallow_empty() -> None:
    """Test empty `Disallow`."""

    disallow = Disallow()
    assert not list(disallow.search_on_src("lambda x: x"))


def test_disallow_count() -> None:
    """Test `Disallow` on string count."""

    disallow = Disallow(functions=["count"])
    assert list(disallow.search_on_src("lambda s: s.count('a')")) == [("count", 1)]
    assert not list(disallow.search_on_src("lambda s: s.index('a')"))


def test_disallow_div() -> None:
    """Test `Disallow` on floating-point division."""

    disallow = Disallow(binops=[ast.Div])
    assert list(disallow.search_on_src("lambda a, b: a / b")) == [("Div", 1)]
    assert not list(disallow.search_on_src("lambda a, b: a // b"))


def test_disallow_plus_eq() -> None:
    """Test `Disallow` on +=."""

    disallow = Disallow(binops=[ast.Add])
    assert list(disallow.search_on_src("def foo(a, b):\n    a += b")) == [("Add", 2)]
    assert list(disallow.search_on_src("lambda a, b: a + b")) == [("Add", 1)]
    assert not list(disallow.search_on_src("lambda a, b: a * b"))
