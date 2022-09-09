from aga import problem, test_case, test_cases


@test_cases(
    [
        "alice",
        "carol",
        "dave",
        "eve",
    ],
    aga_expect_stdout=[
        ["What is your name? ", f"Hello, world! {name}!"]
        for name in [
            "alice",
            "carol",
            "dave",
            "eve",
        ]
    ],
)
@test_case("Bob", aga_expect_stdout=["What is your name? ", "Hello, world! Bob!"])
@problem(script=True)
def hello_world() -> None:
    """Print 'Hello, world!'."""
    name = input("What is your name? ")
    print(f"Hello, world! {name}!")


# you can check with `aga check input_and_expect_output_script.py`
hello_world.check()
