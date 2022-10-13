"""Test aga core module."""

from __future__ import annotations

from typing import Dict

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

    def test_aga_test_cases_no_flag_fail(self) -> None:
        """Test that aga_test_cases without a combination flag raises an error."""
        with pytest.raises(
            ValueError,
            match="Exactly one of aga_product, aga_zip, or aga_params must be True.",
        ):

            @_test_cases([1, 2])
            @problem()
            def test_problem(x: int) -> int:
                """Test problem."""
                return x

    @pytest.mark.parametrize(
        "flags",
        [
            {"aga_product": True, "aga_zip": True, "aga_params": True},
            {"aga_zip": True, "aga_params": True},
            {"aga_product": True, "aga_params": True},
            {"aga_product": True, "aga_zip": True},
        ],
    )
    def test_aga_test_cases_multiple_flags_fail(self, flags: Dict[str, bool]) -> None:
        """Test that aga_test_cases with multiple combination flags raises an error."""
        with pytest.raises(
            ValueError,
            match="Exactly one of aga_product, aga_zip, or aga_params must be True.",
        ):

            @_test_cases([1, 2], **flags)
            @problem()
            def test_problem(x: int) -> int:
                """Test problem."""
                return x

    def test_aga_params_with_kwargs(self) -> None:
        """Test that aga_params can be used with kwargs."""
        with pytest.raises(ValueError, match="aga_params=True ignores non-aga kwargs"):

            @_test_cases_params(
                [param(1, 2, c=3), param(4, 5, c=6)], k=10, aga_expect=[6, 15]
            )
            @problem()
            def add_two(x: int, y: int) -> int:
                """Add two numbers."""
                return x + y

    def test_aga_params_with_multiple_args(self) -> None:
        """Test that aga_params can be used with multiple args."""
        with pytest.raises(
            ValueError,
            match="aga_params=True requires exactly one iterable of sets of parameters",
        ):

            @_test_cases_params(
                [param(1, 2, c=3)], [param(4, 5, c=6)], aga_expect=[6, 15]
            )
            @problem()
            def add_two(x: int, y: int) -> int:
                """Add two numbers."""
                return x + y
