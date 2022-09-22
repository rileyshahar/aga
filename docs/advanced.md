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
argument to `test_case`. This function takes three arguments: a
`unittest.TestCase` object (which you should use to make assertions), the golden
solution's output, and the student submission output. For example, to test a
higher-order function:

```python
from aga import problem, test_case

def _make_n_check(case, golden, student):
    # here `golden` and `student` are the inner functions returned by the
    # submissions, so they have type int -> int`
    for i in range(10):
        case.assertEqual(golden(i), student(i), f"Solutions differed on input {i}.")

@test_cases([-3, -2, 16, 20], aga_override_check=_make_n_check)
@test_case(0, aga_override_check=_make_n_check)
@test_case(2, aga_override_check=_make_n_check)
@problem()
def make_n_adder(n: int) -> Callable[[int], int]:
    def inner(x: int) -> int:
        return x + n
    return inner
```
