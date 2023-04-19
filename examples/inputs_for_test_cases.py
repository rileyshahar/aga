"""This example shows how to setup inputs for test cases."""
from typing import Tuple

from aga import problem, test_cases, param


# the aga_* kwargs can accept singletons or iterables


# this is the singleton way
# it's intended to work bulk/random test cases
# where `aga_expect` or `aga_expect_stdout` are not present
# `aga_hidden=True` means everything is hidden, which is
# equivalent to `aga_hidden=[True] * 10` in this case
# similar for `aga_value`
@test_cases(*range(10), aga_hidden=True, aga_value=1)
@problem()
def singleton_mode(a: int) -> int:
    """This problem is in singleton mode."""
    return a


# this is the iterable way
# it's intended to work with `aga_expect` or `aga_expect_stdout`
@test_cases(*range(10), aga_expect=range(10))
@problem()
def iterable_mode(a: int) -> int:
    """This problem is in iterable mode."""
    return a


# test_cases
@test_cases((-3, 2), (-2, 1), (0, 0))
@problem()
def difference(tp) -> int:
    """Compute x - y."""
    x, y = tp
    return x - y


@test_cases(1, 2, 3)
@problem()
def square(x) -> int:
    """Compute x - y."""
    return x ** 2


# notice the * before the range
@test_cases(*range(10))
@problem()
def square(x) -> int:
    """Compute x - y."""
    return x ** 2


# test_cases.params
@test_cases.params([param(-3, y=2), param(-2, y=1), param(0, y=0)])
@problem()
def difference(x: int, y: int) -> int:
    """Compute x - y."""
    return x - y


# the following is equivalent to the above
@test_cases([(-3, 2), (-2, 1), (0, 0)], aga_params=True)
@problem()
def difference(x: int, y: int) -> int:
    """Compute x - y."""
    return x - y


# note that you cannot write
# but, you can use the `singular_params` option
# @test_cases.params(range(10))    # <===== this is not allowed in this case
# @problem()
# def square(x: int) -> int:
#     """Compute x - y."""
#     return x ** 2


# test_cases.singular_params
@test_cases.singular_params(range(10))
@problem()
def square(x: int) -> int:
    """Compute x - y."""
    return x ** 2


@test_cases.singular_params([ (1, 2, 3), (3, 4), (5, 6, 7, 8) ])
@problem()
def square(num_seq: Tuple[int]) -> int:
    """Compute x - y."""
    return sum(num_seq)


# test_cases.product
@test_cases.product([-5, 0, 1, 3, 4], [-1, 0, 2])
@problem()
def difference(x: int, y: int) -> int:
    """Compute x - y."""
    return x - y


# test_cases.zip
@test_cases.zip([-5, 0, 1, 3, 4], [-1, 0, 2])
@problem()
def difference(x: int, y: int) -> int:
    """Compute x - y."""
    return x - y
