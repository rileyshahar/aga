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
    Callable,
    TypedDict,
    cast,
    overload,
    Sequence,
)
from enum import Enum


if TYPE_CHECKING:
    from .problem import Problem, ProblemParamSpec, ProblemOutputType


# pylint: disable=C0103
class AgaReservedKeywords(Enum):
    """Reserved keywords for aga."""

    aga_expect = "aga_expect"
    aga_expect_stdout = "aga_expect_stdout"
    aga_hidden = "aga_hidden"
    aga_name = "aga_name"
    aga_weight = "aga_weight"
    aga_value = "aga_value"
    aga_extra_credit = "aga_extra_credit"
    aga_override_check = "aga_override_check"
    aga_override_test = "aga_override_test"
    aga_description = "aga_description"
    aga_is_pipeline = "aga_is_pipeline"


DEFAULT_AGA_RESERVED_VALUES = {
    "aga_expect": None,
    "aga_expect_stdout": None,
    "aga_hidden": False,
    "aga_name": None,
    "aga_weight": 1,
    "aga_value": 0.0,
    "aga_extra_credit": 0.0,
    "aga_override_check": None,
    "aga_override_test": None,
    "aga_description": None,
    "aga_is_pipeline": False,
}


class AgaKeywordDictType(TypedDict):
    """Aga keyword arguments type."""

    aga_expect: None | Any
    aga_expect_stdout: None | str
    aga_hidden: bool
    aga_name: None | str
    aga_weight: int
    aga_value: float
    aga_extra_credit: float
    aga_override_check: None | Callable[..., bool]
    aga_override_test: None | Callable[..., Any]
    aga_description: None | str
    aga_is_pipeline: bool


__all__ = [
    "test_case",
    "param",
    "test_cases",
    "test_cases_params",
    "test_cases_zip",
    "test_cases_product",
    "test_cases_singular_params",
    "AgaReservedKeywords",
    "AgaKeywordContainer",
]


def _check_default_values() -> None:
    """Raise an error if `kwd` is reserved."""
    assert len(AgaReservedKeywords) == len(DEFAULT_AGA_RESERVED_VALUES)
    for kwd in AgaReservedKeywords:
        assert kwd.value in DEFAULT_AGA_RESERVED_VALUES


_check_default_values()


class AgaKeywordContainer:
    """A container for aga_* keyword arguments."""

    def __init__(self, **kwargs: Any):
        self.aga_kwargs: AgaKeywordDictType = cast(AgaKeywordDictType, kwargs)

    @property
    def aga_kwargs(self) -> AgaKeywordDictType:
        """Return the aga_* keyword arguments of the test."""
        return self._aga_kwargs

    @aga_kwargs.setter
    def aga_kwargs(self, kwargs: AgaKeywordDictType) -> None:
        """Set the aga_* keyword arguments of the test."""
        self._aga_kwargs = kwargs
        self.ensure_aga_kwargs()

    def ensure_aga_kwargs(self) -> AgaKeywordContainer:
        """Ensure that the aga_* keywords are handled correct."""
        for k in self.aga_kwargs:
            try:
                AgaReservedKeywords(k)
            except ValueError as e:
                raise ValueError(f'invalid kwargs "{k}" in a test param') from e
        return self

    def update_aga_kwargs(self, **kwargs: Any) -> AgaKeywordContainer:
        """Update the keyword arguments to be passed to the functions under test."""
        self.aga_kwargs.update(kwargs)  # type: ignore
        self.ensure_aga_kwargs()
        return self

    def ensure_default_aga_values(self) -> AgaKeywordContainer:
        """Ensure that the aga_* keywords all have default."""
        self.aga_kwargs = cast(
            AgaKeywordDictType, {**DEFAULT_AGA_RESERVED_VALUES, **self.aga_kwargs}
        )
        return self

    @property
    def description(self) -> str | None:
        """Get the description of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_description.value]

    @description.setter
    def description(self, desc: str | None) -> None:
        """Set the description of the test case."""
        self.aga_kwargs[AgaReservedKeywords.aga_description.value] = desc

    @property
    def name(self) -> str | None:
        """Get the name of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_name.value]

    @name.setter
    def name(self, name: str | None) -> None:
        """Set the name of the test case."""
        self.aga_kwargs[AgaReservedKeywords.aga_name.value] = name

    @property
    def override_test(self) -> Callable[..., Any] | None:
        """Get the override_test aga_override_test of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_override_test.value]

    @property
    def override_check(self) -> Callable[..., Any] | None:
        """Get the override_check aga_override_check of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_override_check.value]

    @property
    def is_pipeline(self) -> bool:
        """Get the is_pipeline aga_is_pipeline of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_is_pipeline.value]

    @property
    def weight(self) -> int:
        """Get the weight aga_weight of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_weight.value]

    @property
    def value(self) -> float:
        """Get the value aga_value of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_value.value]

    @property
    def extra_credit(self) -> float:
        """Get the extra credit aga_extra_credit of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_extra_credit.value]

    @property
    def hidden(self) -> bool:
        """Get the hidden aga_hidden of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_hidden.value]

    @property
    def expect(self) -> Any:
        """Get the expected aga_expect of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_expect.value]

    @property
    def expect_stdout(self) -> str | None:
        """Get the expected aga_expect_stdout of the test case."""
        return self.aga_kwargs[AgaReservedKeywords.aga_expect_stdout.value]

    def aga_kwargs_repr(self, sep: str = ",") -> str:
        """Return a string representation of the test's aga_* keyword arguments."""
        return sep.join(k + "=" + repr(v) for k, v in self.aga_kwargs.items())


class _TestParam(AgaKeywordContainer):
    __slots__ = ["_args", "_kwargs", "_aga_kwargs"]

    pipeline: ClassVar[partial[_TestParam]]

    @overload
    def __init__(
        self,
        *args: Any,
        aga_expect: Any = None,
        aga_expect_stdout: str | Sequence[str] | None = None,
        aga_hidden: bool = False,
        aga_name: str | None = None,
        aga_description: str | None = None,
        aga_weight: int = 1,
        aga_value: float = 0.0,
        aga_extra_credit: float = 0.0,
        aga_override_check: Callable[..., Any] | None = None,
        aga_override_test: Callable[..., Any] | None = None,
        aga_is_pipeline: bool = False,
        **kwargs: Any,
    ) -> None:
        ...

    @overload
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
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
        aga_is_pipeline: bool
            If True, the test case will be run through as a pipeline.
        kwargs :
            Keyword arguments to be passed to the functions under test. Any keyword
            starting with aga\_ is reserved.

        Returns
        -------
        Callable[[Problem[T]], Problem[T]]
            A decorator which adds the test case to a problem.
        """
        super().__init__(
            **{
                k.value: kwargs.pop(k.value)
                for k in AgaReservedKeywords
                if k.value in kwargs
            }
        )
        self.kwargs = kwargs
        self.args = args

    @property
    def args(self) -> Tuple[Any, ...]:
        """Return the arguments to be passed to the functions under test."""
        return self._args

    @args.setter
    def args(self, args: Tuple[Any, ...]) -> None:
        """Set the arguments to be passed to the functions under test."""
        self._args = args

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Return the keyword arguments to be passed to the functions under test."""
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs: Dict[str, Any]) -> None:
        """Set the keyword arguments to be passed to the functions under test."""
        self._kwargs = kwargs
        self.ensure_valid_kwargs()

    def ensure_valid_kwargs(self) -> _TestParam:
        """Ensure that the aga_* keywords are handled correct."""
        for k in self.kwargs:
            if k.startswith("aga_"):
                raise ValueError(
                    f'aga keyword "{k}" should not be in kwargs of a test param'
                )
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

    def generate_test_case(
        self, prob: Problem[ProblemParamSpec, ProblemOutputType]
    ) -> Problem[ProblemParamSpec, ProblemOutputType]:
        """Generate a test case for the given problem."""
        self.ensure_default_aga_values()
        self.ensure_valid_kwargs().ensure_aga_kwargs()  # type: ignore

        prob.add_test_case(param=self)

        return prob

    def __call__(
        self, prob: Problem[ProblemParamSpec, ProblemOutputType]
    ) -> Problem[ProblemParamSpec, ProblemOutputType]:
        """Add the test case to the given as a decorator."""
        return self.generate_test_case(prob)

    def __str__(self) -> str:
        """Return a string representation of the test case."""
        return f"param({self.args_repr()}, {self.kwargs_repr()})"

    def __repr__(self) -> str:
        """Return a string representation of the test case."""
        return (
            f"param({self.args_repr()}, {self.kwargs_repr()}, {self.aga_kwargs_repr()})"
        )


_TestParam.pipeline = partial(
    _TestParam, aga_is_pipeline=True
)  # pylint: disable=invalid-name
param = _TestParam  # pylint: disable=invalid-name
test_case = _TestParam  # pylint: disable=invalid-name


class _TestParams:
    """A class to store the parameters for a test."""

    __slots__ = ["final_params"]

    params: ClassVar[partial[_TestParams]]
    zip: ClassVar[partial[_TestParams]]
    product: ClassVar[partial[_TestParams]]
    singular_params: ClassVar[partial[_TestParams]]

    # pylint: disable=too-many-locals
    @overload
    def __init__(
        self,
        *args: Any,
        aga_expect: Any = None,
        aga_expect_stdout: str | Sequence[str] | None = None,
        aga_hidden: bool = False,
        aga_name: str | None = None,
        aga_description: str | None = None,
        aga_weight: int = 1,
        aga_value: float = 0.0,
        aga_extra_credit: float = 0.0,
        aga_override_check: Callable[..., Any] | None = None,
        aga_override_test: Callable[..., Any] | None = None,
        aga_is_pipeline: bool = False,
        aga_product: bool = False,
        aga_zip: bool = False,
        aga_params: bool = False,
        aga_singular_params: bool = False,
        **kwargs: Any,
    ):
        ...

    @overload
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def __init__(
        self,
        *args: Iterable[Any] | Any,
        aga_product: bool = False,
        aga_zip: bool = False,
        aga_params: bool = False,
        aga_singular_params: bool = False,
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
        aga_singular_params : bool
            Whether to treat the input generators as a single iterable of single params.
            Default `False`.
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
        if aga_params + aga_zip + aga_product + aga_singular_params > 1:
            raise ValueError(
                "Exactly many of aga_product, aga_zip, or aga_params are True. "
                "Only 0 or 1 of the flags is allowed. \n"
                f"You got: "
                f"aga_product={aga_product}, aga_zip={aga_zip}, aga_params={aga_params}"
            )

        # pop aga keywords out
        aga_kwargs_dict = {
            kwd.value: kwargs.pop(kwd.value)
            for kwd in AgaReservedKeywords
            if kwd.value in kwargs
        }

        if aga_params:
            # build final params
            # So we're allowing [param(1, 2), [3, 4]] as a valid input
            self.final_params: List[_TestParam] = type(self).parse_params(
                *args, **kwargs
            )
        elif aga_singular_params:
            self.final_params = type(self).parse_singular_params(*args, **kwargs)
        elif aga_zip or aga_product:
            self.final_params = type(self).parse_zip_or_product(
                *args, aga_zip=aga_zip, aga_product=aga_product, **kwargs
            )
        else:
            self.final_params = type(self).parse_no_flag(*args, **kwargs)

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
    def parse_singular_params(*args: Iterable[Any], **kwargs: Any) -> List[_TestParam]:
        """Parse the parameters for param sequence."""
        if kwargs:
            raise ValueError("aga_singular_params=True ignores non-aga kwargs")

        if len(args) != 1:
            raise ValueError(
                "aga_singular_params=True requires "
                "exactly one iterable of sets of parameters"
            )

        return list(
            arg if isinstance(arg, _TestParam) else param(arg) for arg in args[0]
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
    def parse_no_flag(*args: Iterable[Any], **kwargs: Any) -> List[_TestParam]:
        """Parse the parameters for no flag."""
        if kwargs:
            raise ValueError("`test_cases` with no flags ignores non-aga kwargs")

        return [param(arg) for arg in args]

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

    def __call__(
        self, prob: Problem[ProblemParamSpec, ProblemOutputType]
    ) -> Problem[ProblemParamSpec, ProblemOutputType]:
        """Generate the test cases as a decorator."""
        for final_param in self.final_params:
            prob = final_param.generate_test_case(prob)

        return prob


test_cases = _TestParams  # pylint: disable=invalid-name
test_cases_params = partial(test_cases, aga_params=True)
test_cases_zip = partial(test_cases, aga_zip=True)
test_cases_product = partial(test_cases, aga_product=True)
test_cases_singular_params = partial(test_cases, aga_singular_params=True)
test_cases.params = test_cases_params
test_cases.product = test_cases_product
test_cases.zip = test_cases_zip
test_cases.singular_params = test_cases_singular_params
