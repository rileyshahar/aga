from aga import problem, test_case


@test_case(10, 20, aga_expect_stdout="the result is 30\n")
@problem(check_stdout=True)
def add(a: int, b: int) -> int:
    """Add two numbers."""
    print("the result is", a + b)
    return a + b


add.check()
