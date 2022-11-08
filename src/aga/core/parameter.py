"""Parameter wrappers."""
from __future__ import annotations

from collections.abc import Iterable
from functools import partial
from itertools import product
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    ClassVar,
    TYPE_CHECKING,
    TypeVar,
)

Output = TypeVar("Output")


if TYPE_CHECKING:
    from .problem import Problem

AGA_RESERVED_KEYWORDS = {
    "aga_expect",
    "aga_expect_stdout",
    "aga_hidden",
    "aga_name",
    "aga_weight",
    "aga_value",
    "aga_extra_credit",
    "aga_override_check",
    "aga_override_test",
    "aga_description",
}


__all__ = [
    "test_case",
    "param",
    "test_cases",
    "test_cases_params",
    "test_cases_zip",
    "test_cases_product",
]


def _check_reserved_keyword(kwd: str) -> None:
    """Raise an error if `kwd` is reserved."""
    if kwd.startswith("aga_") and kwd not in AGA_RESERVED_KEYWORDS:
        raise ValueError(
            f'invalid keyword arg "{kwd}" to `test_case`: all keyword args '
            "beginning `aga_` are reserved"
        )


class _TestParam:
    __slots__ = ["_args", "_kwargs", "_aga_kwargs"]

    def __init__(self, *args: Any, **kwargs: Any):
        r"""Declare a specific test case/param for some problem.

        Parameters
        ----------
        args :
            The arguments to be passed to the functions under test.
        aga_expect : Optional[T]
            If aga_expect is None, the inputs will be tested against the wrapped
            function, the "golden solution" to the problem. If aga_expect is
            specified, the inputs will double as a test _of_ the golden solution;
            to successfully produce the problem grader, the golden solution must
            return aga_expect from the given input.
        aga_expect_stdout : Optional[str | Sequence[str]]
            If aga_expect_stdout is specified, the golden solution's stdout will be
            checked against the given value(s). If aga_expect_stdout is a string, it
            will be compared against the golden solution's stdout. If
            aga_expect_stdout is a sequence of strings, the golden solution's stdout
            will be split on newlines (with '\n' removed) and the resulting list will
            be compared against the given sequence. If aga_expect_stdout is None, the
            golden solution's stdout will not be checked.
        aga_hidden : bool
            If True, hide the problem from students on supported frontends.
        aga_name : Optional[str]
            The test case's name. If `None`, defaults to "Test {inputs}", where
            {inputs} is a comma-separated list of args and kwargs.
        aga_description: Optional[str]
            The detailed description for the test case. It will be displayed under the
            test case name and thus supports longer descriptions.
        aga_weight : int
            The test case's relative weight to the group's score. See :ref:`Determining
            Score` for details.
        aga_value : float
            The test case's absolute score. See :ref:`Determining Score` for details.
        aga_extra_credit : float
            The test case's absolute extra credit score. See :ref:`Determining Score`
            for details.
        aga_override_check : Callable[[TestCase, Output, T], None] | None
            A function which overrides the equality assertions made by the library. See
            :ref:`Overriding the Equality Check` for more.
        aga_override_test : Callable[[TestCase, Callable[T], Callable[T]], None] | None
            A function which overrides the entire test behavior of the library. See
            :ref:`Overriding the Entire Test` for more.
        kwargs :
            Keyword arguments to be passed to the functions under test. Any keyword
            starting with aga\_ is reserved.

        Returns
        -------
        Callable[[Problem[T]], Problem[T]]
            A decorator which adds the test case to a problem.
        """
        self._args = args
        self._kwargs = kwargs
        self._aga_kwargs = {
            k: kwargs.pop(k) for k in AGA_RESERVED_KEYWORDS if k in kwargs
        }

    @property
    def args(self) -> Tuple[Any, ...]:
        """Return the arguments to be passed to the functions under test."""
        return self._args

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Return the keyword arguments to be passed to the functions under test."""
        return self._kwargs

    @property
    def aga_kwargs(self) -> Dict[str, Any]:
        """Return the aga_* keyword arguments of the test."""
        return self._aga_kwargs

    def update_aga_kwargs(self, **kwargs: Any) -> _TestParam:
        """Update the keyword arguments to be passed to the functions under test."""
        self._aga_kwargs.update(kwargs)
        return self

    def args_repr(self, sep: str = ",") -> str:
        """Return a string representation of the test's arguments."""
        return sep.join(repr(x) for x in self.args)

    def kwargs_repr(self, sep: str = ",") -> str:
        """Return appropriate string representation of the test's keyword arguments."""
        # we use k instead of repr(k) so we don't get quotes around it
        return sep.join(k + "=" + repr(v) for k, v in self.kwargs.items())

    def sep_repr(self, sep: str = ",") -> str:
        """Return sep if both exist, "" otherwise."""
        return self.args and self.kwargs and sep or ""

    def generate_test_case(self, prob: Problem[Output]) -> Problem[Output]:
        """Generate a test case for the given problem."""
        self.check_validity()

        prob.add_test_case(
            aga_param=self,
            **self._aga_kwargs,
        )

        return prob

    def check_validity(self) -> None:
        """Check if the test case is valid."""
        # check that kwargs doesn't contain any reserved keywords
        for kwd in self.kwargs:
            _check_reserved_keyword(kwd)

    def __call__(self, prob: Problem[Output]) -> Problem[Output]:
        """Add the test case to the given problem."""
        return self.generate_test_case(prob)

    def __str__(self) -> str:
        """Return a string representation of the test case."""
        return f"TestCase({self.args}, {self.kwargs})"

    def __repr__(self) -> str:
        """Return a string representation of the test case."""
        return f"TestCase({self.args}, {self.kwargs}, {self.aga_kwargs})"


param = _TestParam  # pylint: disable=invalid-name
test_case = _TestParam  # pylint: disable=invalid-name


class _TestParams:
    """A class to store the parameters for a test."""

    __slots__ = ["final_params"]

    params: ClassVar[partial[_TestParams]]
    zip: ClassVar[partial[_TestParams]]
    product: ClassVar[partial[_TestParams]]

    def __init__(
        self,
        *args: Iterable[Any],
        aga_product: bool = False,
        aga_zip: bool = False,
        aga_params: bool = False,
        **kwargs: Any,
    ) -> None:
        r"""Generate many test cases programmatically, from generators of inputs.

        Parameters
        ----------
        args :
            Generators for arguments to be passed to the functions under test.
        aga_product : bool
            Whether to take a cartesian product of the generators (creating one test
            case for each set of inputs in the product), or to zip them (iterate
            through each generator in sequence). Default `False`.
        aga_zip : bool
            Whether to zip the input generators. Default `False`.
        aga_params : bool
            Whether to treat the input generators as a single iterable of sets of
            parameters. Default `False`.
        kwargs :
            `aga_` keywords have their meaning inherited from `test_case`, and are
            applied to each test case generated by this function. Singleton value and
            Sequence values are supported, i.e., `aga_hidden=True` and
            `aga_expect = [1, 2, 3]` are both valid. When passing in a Sequence object,
            the length of the sequence must match the length of the test cases.
            Generators for keyword arguments to be passed to the functions under test.
            Any keyword starting with aga\_ is reserved.

        Returns
        -------
        Callable[[Problem[T]], Problem[T]]
            A decorator which adds the test cases to a problem.
        """
        if not (aga_product ^ aga_zip ^ aga_params) or (
            aga_product and aga_zip and aga_params
        ):
            raise ValueError(
                "Exactly one of aga_product, aga_zip, or aga_params must be True. \n"
                f"You got: "
                f"aga_product={aga_product}, aga_zip={aga_zip}, aga_params={aga_params}"
            )

        # pop aga keywords out
        aga_kwargs_dict = {
            kwd: kwargs.pop(kwd) for kwd in AGA_RESERVED_KEYWORDS if kwd in kwargs
        }

        if aga_params:
            # build final params
            # So we're allowing [param(1, 2), [3, 4]] as a valid input
            self.final_params: List[_TestParam] = type(self).parse_params(
                *args, **kwargs
            )
        else:
            self.final_params = type(self).parse_zip_or_product(
                *args, aga_zip=aga_zip, aga_product=aga_product, **kwargs
            )

        type(self).add_aga_kwargs(aga_kwargs_dict, self.final_params)

    @staticmethod
    def parse_params(*args: Iterable[Any], **kwargs: Any) -> List[_TestParam]:
        """Parse the parameters for param sequence."""
        if kwargs:
            raise ValueError("aga_params=True ignores non-aga kwargs")

        if len(args) != 1:
            raise ValueError(
                "aga_params=True requires exactly one iterable of sets of parameters"
            )

        return list(
            arg if isinstance(arg, _TestParam) else param(*arg) for arg in args[0]
        )

    @staticmethod
    def parse_zip_or_product(
        *args: Iterable[Any],
        aga_product: bool = False,
        aga_zip: bool = False,
        **kwargs: Any,
    ) -> List[_TestParam]:
        """Parse parameters for zip or product."""
        if not aga_zip ^ aga_product:
            raise ValueError("exactly one of aga_zip or aga_product must be True")
        combinator = product if aga_product else zip

        # ok so if the combinator is product
        # we are taking the cartesian product for all args and kwargs
        # and if the combinator is zip,
        # we are zipping all the args and kwargs, if there are any
        combined_args = list(combinator(*args))
        combined_kwargs = list(combinator(*kwargs.values()))

        # ======= validation checks =======
        if combinator is zip:
            # create empty args for zip if there are no args
            if combined_args and combined_kwargs:
                if len(combined_args) != len(combined_kwargs):
                    raise ValueError(
                        'length of "args" and "kwargs" must match in zip mode'
                    )
            elif combined_args:
                combined_kwargs = [()] * len(combined_args)
            elif combined_kwargs:
                combined_args = [()] * len(combined_kwargs)

        all_args_and_kwargs = list(combinator(combined_args, combined_kwargs))

        # ======= zipping all the args together =======
        return list(
            param(*curr_args, **dict(zip(kwargs.keys(), curr_kwargs)))
            for (curr_args, curr_kwargs) in all_args_and_kwargs
        )

    @staticmethod
    def add_aga_kwargs(
        aga_kwargs: Dict[str, Any], final_params: List[_TestParam]
    ) -> None:
        """Add aga_kwargs to the finalized parameters."""
        # process aga input type
        for aga_kwarg_key, aga_kwarg_value in aga_kwargs.items():
            if isinstance(aga_kwarg_value, Iterable) and not isinstance(
                aga_kwarg_value, str
            ):
                aga_kwargs[aga_kwarg_key] = list(aga_kwarg_value)
            else:
                aga_kwargs[aga_kwarg_key] = [aga_kwarg_value] * len(final_params)

        # validate aga input type
        if not all(
            len(aga_kwarg_value) == len(final_params)
            for aga_kwarg_value in aga_kwargs.values()
        ):
            # the length of the kwargs should be equal to the number of test cases
            # i.e. the length of the combined args
            raise ValueError(
                f"all aga_ keyword args must have the same length as the test cases, "
                f"which is {len(final_params)}"
            )

        # the aga kwargs list we want
        aga_kwargs_list: List[Dict[str, Any]] = [
            dict(zip(aga_kwargs.keys(), aga_kwarg_value))
            for aga_kwarg_value in zip(*aga_kwargs.values())
        ]

        if not aga_kwargs_list:
            # generate default aga kwargs dict if there are no aga kwargs
            aga_kwargs_list = [{} for _ in final_params]

        for final_param, kwargs in zip(final_params, aga_kwargs_list):
            final_param.update_aga_kwargs(**kwargs)

    def __call__(self, prob: Problem[Output]) -> Problem[Output]:
        for final_param in self.final_params:
            prob = final_param.generate_test_case(prob)

        return prob


test_cases = _TestParams  # pylint: disable=invalid-name
test_cases_params = partial(test_cases, aga_params=True)
test_cases_zip = partial(test_cases, aga_zip=True)
test_cases_product = partial(test_cases, aga_product=True)
test_cases.params = test_cases_params
test_cases.product = test_cases_product
test_cases.zip = test_cases_zip
