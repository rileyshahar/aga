"""Test aga core module."""

from __future__ import annotations

import pytest
from aga import test_cases, problem


# pylint: disable=no-self-use
class TestTestCases:
    """Test the test_cases decorator."""

    def test_zip_arg_length_and_kwargs_length_not_match(self) -> None:
        """Test that the length of the zipped args and kwargs must match."""

        with pytest.raises(
            ValueError, match='length of "args" and "kwargs" must match in zip mode'
        ):

            @test_cases(range(2), y=range(3), aga_product=False)
            @problem()
            def test_problem(x: int, y: int) -> int:  # pragma: no cover
                return x * y

    def test_only_kwargs(self) -> None:
        """Test that test cases only have kwargs."""

        @test_cases(
            x=range(3),
            y=range(3),
            aga_product=False,
            aga_expect=map(lambda x: x * x, range(3)),
        )
        @problem()
        def test_problem(x: int, y: int) -> int:
            return x * y

        test_problem.check()

    def test_invalid_aga_kwargs(self) -> None:
        """Test that invalid aga_* keyword args raise an error."""
        with pytest.raises(
            ValueError,
            match="invalid aga_ keyword arg: "
            "must all be sequences or singletons, not mixed",
        ):

            @test_cases(
                x=range(3),
                y=range(3),
                aga_product=False,
                aga_expect=map(lambda x: x * x, range(3)),
                aga_hidden=True,
            )
            @problem()
            def test_problem(x: int, y: int) -> int:  # pragma: no cover
                return x * y

    def test_aga_kwargs_length_not_match(self) -> None:
        """Test that the length of the aga_* keyword args must match."""
        with pytest.raises(
            ValueError,
            match="all aga_ keyword args must have the same length as the test cases",
        ):

            @test_cases(
                x=range(3),
                y=range(3),
                aga_product=False,
                aga_expect=map(lambda x: x * x, range(3)),
                aga_hidden=[True] * 10,
            )
            @problem()
            def test_problem(x: int, y: int) -> int:  # pragma: no cover
                return x * y
