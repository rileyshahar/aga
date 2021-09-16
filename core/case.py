"""Contains the test_case decorator.

This is called `case.py` instead of `test_case.py` so that pytest doesn't think
this is a test module.
"""

from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

if TYPE_CHECKING:
    from .problem import Problem

O = TypeVar("O")


def test_case(
    *args, output: Optional[Any] = None, **kwargs
) -> Callable[["Problem[O]"], "Problem[O]"]:
    """Declare a specific test case for some problem.

    If `output` is None, the inputs will be tested against the wrapped function,
    the "golden solution" to the problem. If `output` is specified, the inputs
    will double as a test _of_ the golden solution; to successfully produce the
    problem grader, the golden solution must return output from the given input.
    """

    def outer(problem: "Problem[O]") -> "Problem[O]":
        if output is not None:
            problem.add_golden_test_case(GoldenTestCase(output, *args, *kwargs))
            return problem

        else:
            problem.add_test_case(*args, **kwargs)
            return problem

    return outer


class TestCase:
    def __init__(self, *args, **kwargs) -> None:

        self._args: tuple = args
        self._kwargs: dict = kwargs

    def _eval(self, func: Callable[..., O]) -> O:
        """Evaluate func on the arguments."""
        return func(*self._args, **self._kwargs)

    def check(self, golden: Callable[..., O], under_test: Callable[..., O]) -> bool:
        """Compare the output of `golden` to that of `under_test`.

        Returns `true` if the test succeeded (the outputs were identical),
        `false` otherwise.

        TODO: This should return more detailed information about the failure.
        """
        return self._eval(golden) == self._eval(under_test)


class GoldenTestCase(TestCase):
    def __init__(self, output: O, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)
        self._output = output

    def check_one(self, under_test: Callable[..., O]) -> bool:
        """Compare the output of `under_test` to the test case's golden output.

        Returns `true` if the test succeeded (the output was identical), `false`
        otherwise.

        TODO: This should return more detailed information about the failure.
        """
        return self._eval(under_test) == self._output

    def check(self, golden: Callable[..., O], under_test: Callable[..., O]) -> bool:
        """Compare the output of `golden` to `under_test` and the golden output.

        Returns `true` if all three match, `false` otherwise.

        TODO: This should return more detailed information about the failure.
        """
        return self.check_one(golden) and super().check(golden, under_test)
