# Advanced Features

## Prizes

If you want finer control over the points allocation of problems, you can add
points prizes to them, which let you run custom functions over the list of
completed tests in order to assign points values:

```python
from aga import problem, test_case
from aga.prize import prize, TcOutput, SubmissionMetadata

def all_correct(
    tests: list[TcOutput], _: SubmissionMetadata
) -> tuple[float, str]:
"""Check that all tests passed."""
    if all(t.is_correct() for t in tests):
        return 1.0, "Good work! You earned these points since all tests passed."
    else:
        return 0.0, "To earn these points, make sure all tests pass."

@prize(all_correct, name="Prize")
@test_case(0)
@test_case(2)
@problem()
def square(x: int) -> int:
    """Square x."""
		return x * x
```

If only one of the `0` or `2` test cases pass, the student will receive 1/3
credit for this problem. If both pass, they will receive full credit.

We provide more details and several pre-written prize functions in the
`prize`(reference.html#module-aga.prize) documentation.

## Overriding the Equality Check

By default, `aga` uses unittest's `assertEqual`, or `assertAlmostEqual` for
floats, to test equality. This can be overridden with the `aga_override_check`
argument to `test_case`. This argument takes a function of three arguments: a
`unittest.TestCase` object (which you should use to make assertions), the golden
solution's output, and the student submission output. For example, to test a
higher-order function:

```python
from typing import Callable

from aga import problem, test_case

def _make_n_check(case, golden, student):
    # here `golden` and `student` are the inner functions returned by the
    # submissions, so they have type int -> int`
    for i in range(10):
        case.assertEqual(golden(i), student(i), f"Solutions differed on input {i}.")

@test_cases(-3, -2, 16, 20, aga_override_check=_make_n_check)
@test_case(0, aga_override_check=_make_n_check)
@test_case(2, aga_override_check=_make_n_check)
@problem()
def make_n_adder(n: int) -> Callable[[int], int]:
    def inner(x: int) -> int:
        return x + n
    return inner
```

## Overriding the Entire Test
If you want even more granular control, you can also override the entire test.
The `aga_override_test` argument to `test_case` takes a function of three
arguments: the same `unittest.TestCase` object, the golden solution (the
solution itself, _not_ its output), and the student solution (ditto). For
example, to mock some library:

```python
from unittest.mock import patch

from aga import problem, test_case


def mocked_test(case, golden, student):
    with patch("foo") as mocked_foo:
        case.assertEqual(golden(0), student(0), "test failed")


@test_case(aga_override_test=mocked_test)
@problem()
def call_foo(n):
    foo(n)
```

A common use-case is to disallow the use of certain constructs. For
convenience, `aga` provides the
[`Disallow`](reference.html#aga.checks.Disallow) class. For example, to force
the student to use a `lambda` instead of a `def`:

```python
import ast

from aga import problem, test_case
from aga.checks import Disallow

# I recommend you use `aga_name` here, because the generated one won't be very good
@test_case(
    aga_name="Use lambda, not def!",
    aga_override_test=Disallow(nodes=[ast.FunctionDef]).to_test()
)
@problem()
def is_even_lambda(x: int) -> bool:
    return x % 2 == 0
```

For full details on `Disallow`, see the reference.

If you wish to write your own checks, you can use the methods provided by [`unittest.TestCase`](https://docs.python.org/3/library/unittest.html#unittest.TestCase). For example, the override function can be written as:

```python
def my_check(case, golden, student):
    case.assertEqual(golden(*case.args), student(*case.args), "test failed")
```

The `case` exposes `args` arguments and `kwargs` variables which are passed from `test_case` decorator. For example, `test_case(3, 4, z = 10)` will create a case with `args = (3, 4)` and `kwargs = {"z": 10}`. All the `aga_*` kwargs will be strip away in the building process. 

The `case` also exposes `name` and `description` variables which are the name of the test case and the description of the test case. Changing those variables is equivalent to changing `aga_name` and `aga_description` but this means you can set it dynamically during the testing. 


## Capture Context Values 

Sometimes a piece of assignment file includes multiple classes, and even though only one class is eventually tested, the other parts of students' answers can be crucial. For example, consider the following file. You can specify in the `ctx` argument of `problem` decorator to capture the `GasStation` class, and in the override check function, you can reference the `GasStation` class in the student's answer. 

```python
from aga import problem, test_case

def override_check(case, golden, student):
    # use case.ctx.GasStation to reference student's GasStation class implementation
    ...


@test_case(aga_override_check=override_check)
@problem(ctx=['GasStation'])
class Car:
    # uses gas station somewhere in the code
    ...

class GasStation:
    ...
```

Essentially, `ctx` argument takes in an iterable of strings, and aga will search the corresponding fields in the students' submitted module (file). 
