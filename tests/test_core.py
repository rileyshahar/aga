"""Test aga core module."""

from __future__ import annotations

from typing import Dict, Any, Callable

import pytest
from aga import test_cases as _test_cases
from aga import (
    test_cases_zip as _test_cases_zip,
    test_cases_product as _test_cases_product,
    test_cases_params as _test_cases_params,
    test_cases_singular_params as _test_cases_singular_params,
)
from aga import problem
from aga.core import param, Problem
from aga.core.suite import _TestInputs
from aga.cli.app import _check_problem
from aga.core.utils import CaptureOut


def tester(*_: Any) -> None:
    """Dummy Tester."""


class TestTestCases:
    """Test the test_cases decorator."""

    def test_test_input_with_arguments(self) -> None:
        """Test that test_input can be used with arguments."""
        test_param = param(
            3,
            4,
            y=4,
            aga_expect=True,
            aga_expect_stdout="1",
            aga_hidden=True,
            aga_name="test",
            aga_weight=True,
            aga_value=True,
            aga_extra_credit=True,
            aga_override_check=tester,
            aga_override_test=tester,
            aga_description="test description",
        )
        test_input: _TestInputs[None] = _TestInputs(test_param, mock_input=True)
        assert test_input.param
        assert test_input.args == (3, 4)
        assert test_input.kwargs == {"y": 4}

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

    @pytest.mark.parametrize("test_fn", [_test_cases.params, _test_cases_params])
    def test_aga_params_with_param_obj(
        self, test_fn: Callable[..., Problem[int]]
    ) -> None:
        """Test that aga_params can be used with param objects."""

        @test_fn([param(1, 2, c=3), param(4, 5, c=6)], aga_expect=[6, 15])
        @problem()
        def add_three(a: int, b: int, c: int) -> int:  # pylint: disable=C0103
            """Add three numbers."""
            return a + b + c

        _check_problem(add_three)  # type: ignore

    def test_aga_test_cases_no_flag(self) -> None:
        """Test that aga_test_cases without a combination flag."""

        @_test_cases(1, 2, aga_expect=[1, 4])
        @problem()
        def test_problem(x: int) -> int:
            """Test problem."""
            return x * x

        _check_problem(test_problem)

    def test_aga_test_cases_no_flag_error(self) -> None:
        """Test that aga_test_cases without a combination flag."""

        with pytest.raises(
            ValueError,
            match="all aga_ keyword args must have the same length as the test cases",
        ):

            @_test_cases([1, 2], aga_expect=[1, 4])
            @problem()
            def test_problem(x: int) -> int:
                """Test problem."""
                return x * x

    @pytest.mark.parametrize(
        "test_fn", [_test_cases.singular_params, _test_cases_singular_params]
    )
    def test_aga_test_cases_singular_params(
        self, test_fn: Callable[..., Problem[int]]
    ) -> None:
        """Test that aga_test_cases with aga_params flag."""

        @test_fn(
            [1, 2],
            aga_expect=[1, 4],
        )
        @problem()
        def test_problem(x: int) -> int:
            """Test problem."""
            return x * x

        _check_problem(test_problem)  # type: ignore

    @pytest.mark.parametrize("test_fn", [_test_cases.product, _test_cases_product])
    def test_aga_test_cases_product(self, test_fn: Callable[..., Problem[int]]) -> None:
        """Test that aga_test_cases with aga_params flag."""

        @test_fn(
            [1, 2],
            [3, 4],
            aga_expect=[3, 4, 6, 8],
        )
        @problem()
        def test_problem(x: int, y: int) -> int:
            """Test problem."""
            return x * y

        _check_problem(test_problem)  # type: ignore

    @pytest.mark.parametrize("test_fn", [_test_cases.zip, _test_cases_zip])
    def test_aga_test_cases_zip(self, test_fn: Callable[..., Problem[int]]) -> None:
        """Test that aga_test_cases with aga_params flag."""

        @test_fn(
            [1, 2],
            [3, 4],
            aga_expect=[3, 8],
        )
        @problem()
        def test_problem(x: int, y: int) -> int:
            """Test problem."""
            return x * y

        _check_problem(test_problem)  # type: ignore

    @pytest.mark.parametrize("flags", [{"aga_product": True, "aga_zip": True}, {}])
    def test_zip_or_product_flag_guard(self, flags: Dict[str, bool]) -> None:
        """Test that aga_zip and aga_product are mutually exclusive."""
        with pytest.raises(
            ValueError, match="exactly one of aga_zip or aga_product must be True"
        ):
            _test_cases.parse_zip_or_product(**flags)

    @pytest.mark.parametrize(
        "flags",
        [
            {"aga_product": True, "aga_zip": True, "aga_params": True},
            {"aga_zip": True, "aga_params": True},
            {"aga_product": True, "aga_params": True},
            {"aga_product": True, "aga_zip": True},
            {},
        ],
    )
    def test_aga_test_cases_multiple_flags_fail(self, flags: Dict[str, bool]) -> None:
        """Test that aga_test_cases with multiple combination flags raises an error."""
        with pytest.raises(
            ValueError,
            match="Exactly many of aga_product, aga_zip, or aga_params are True. "
            "Only 1 or 0 of the flags is allowed. ",
        ):

            @_test_cases([1, 2], [3, 4], **flags)
            @problem()
            def test_problem(x: int) -> int:
                """Test problem."""
                return x

    def test_aga_params_with_kwargs(self) -> None:
        """Test that aga_params can be used with kwargs."""
        with pytest.raises(ValueError, match="aga_params=True ignores non-aga kwargs"):

            @_test_cases.params(
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

            @_test_cases.params(
                [param(1, 2, c=3)], [param(4, 5, c=6)], aga_expect=[6, 15]
            )
            @problem()
            def add_two(x: int, y: int) -> int:
                """Add two numbers."""
                return x + y

    def test_capture_out_no_capture(self) -> None:
        """Test that CaptureOut does not capture stdout when taking False."""
        with CaptureOut(False) as stdout:
            print("some stdout")

        assert stdout.value is None

    def test_capture_out_with_capture(self) -> None:
        """Test that CaptureOut captures stdout when taking True."""
        print_value = "some stdout here"
        with CaptureOut(True) as stdout:
            print(print_value, end="")

        assert stdout.value == print_value

    def test_pipeline(self, test_pipeline_linked_list: Problem[None]) -> None:
        """Test that the pipeline decorator works."""
        test_pipeline_linked_list.check()
