"""Test aga core module."""

from __future__ import annotations

import pytest
from aga import test_cases as _test_cases, test_cases_params as _test_cases_params
from aga import problem
from aga.core import param
from aga.cli.app import _check_problem


# pylint: disable=no-self-use
class TestTestCases:
    """Test the test_cases decorator."""

    def test_zip_arg_length_and_kwargs_length_not_match(self) -> None:
        """Test that the length of the zipped args and kwargs must match."""

        with pytest.raises(
            ValueError, match='length of "args" and "kwargs" must match in zip mode'
        ):

            @_test_cases(range(2), y=range(3), aga_zip=True)
            @problem()
            def test_problem(x: int, y: int) -> int:  # pragma: no cover
                return x * y

    def test_only_kwargs(self) -> None:
        """Test that test cases only have kwargs."""

        @_test_cases(
            x=range(3),
            y=range(3),
            aga_zip=True,
            aga_expect=map(lambda x: x * x, range(3)),
        )
        @problem()
        def test_problem(x: int, y: int) -> int:
            return x * y

        test_problem.check()

    def test_different_types_of_aga_kwargs(self) -> None:
        """Test that invalid aga_* keyword args raise an error."""

        @_test_cases(
            x=range(3),
            y=range(3),
            aga_zip=True,
            aga_expect=map(lambda x: x * x, range(3)),
            aga_hidden=True,
        )
        @problem()
        def test_problem(x: int, y: int) -> int:  # pragma: no cover
            return x * y

        test_problem.check()

    def test_aga_kwargs_length_not_match(self) -> None:
        """Test that the length of the aga_* keyword args must match."""
        with pytest.raises(
            ValueError,
            match="all aga_ keyword args must have the same length as the test cases",
        ):

            @_test_cases(
                x=range(3),
                y=range(3),
                aga_zip=True,
                aga_expect=map(lambda x: x * x, range(3)),
                aga_hidden=[True] * 10,
            )
            @problem()
            def test_problem(x: int, y: int) -> int:  # pragma: no cover
                return x * y

    def test_aga_params_with_plain_sequence(self) -> None:
        """Test that aga_params can be used with plain sequences."""

        @_test_cases([(1, 2, 3), (4, 5, 6)], aga_expect=[6, 15], aga_params=True)
        @problem()
        def add_three(a: int, b: int, c: int) -> int:  # pylint: disable=C0103
            """Add three numbers."""
            return a + b + c

        _check_problem(add_three)

    def test_aga_params_with_param_obj(self) -> None:
        """Test that aga_params can be used with param objects."""

        @_test_cases_params([param(1, 2, c=3), param(4, 5, c=6)], aga_expect=[6, 15])
        @problem()
        def add_three(a: int, b: int, c: int) -> int:  # pylint: disable=C0103
            """Add three numbers."""
            return a + b + c

        _check_problem(add_three)
