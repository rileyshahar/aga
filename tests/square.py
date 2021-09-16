from core import problem, test_case


@test_case(4)
@test_case(2, output=4)
@test_case(-2, output=4)
@problem
def square(x: int) -> int:
    """Square x."""
    return x * x
