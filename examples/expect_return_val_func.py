"""This example shows how to use aga expect and aga product."""
from aga import problem, test_case, test_cases


@test_cases(
    [1, 2, 3],
    [4, 5, 6],
    aga_product=False,
    aga_expect=(x + y for x, y in zip([1, 2, 3], [4, 5, 6])),
)
@test_case(10, 20, aga_expect=30)
@problem()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


add.check()

# aga check expect_return_val_func.py
