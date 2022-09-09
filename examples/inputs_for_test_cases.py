"""This example shows how to setup inputs for test cases."""
from aga import problem, test_cases


# the aga_* kwargs can accept singletons or iterables


# this is the singleton way
# it's intended to work bulk/random test cases
# where `aga_expect` or `aga_expect_stdout` are not present
# `aga_hidden=True` means everything is hidden, which is
# equivalent to `aga_hidden=[True] * 10` in this case
# similar for `aga_value`
@test_cases(range(10), aga_hidden=True, aga_value=1)
@problem()
def singleton_mode(a: int) -> int:
    """This problem is in singleton mode."""
    return a


# this is the iterable way
# it's intended to work with `aga_expect` or `aga_expect_stdout`
@test_cases(range(10), aga_expect=range(10))
@problem()
def iterable_mode(a: int) -> int:
    """This problem is in iterable mode."""
    return a
