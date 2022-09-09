from aga import problem, test_case
from aga.prize import prize

# noinspection PyUnresolvedReferences
from aga.injection import prize_fn

# the `prize_fn` is injected from `./aga_injection/jims_prize_function.py`
# you have use options `--inject`, `--inject-dir` or `--auto-inject`
# in aga commands to inject the `prize_fn` function
# for example,
# `aga check --inject-dir ./aga_injection/ injection_support.py`
# `aga check --inject ./aga_injection/jims_prize_function.py injection_support.py`
# `aga check --auto-inject injection_support.py`
# the `check` argument can be replaced with `run` or `gen`

# `--inject <file_path>` is used to inject a single python module
# `--inject-dir <dir_path>` is used to inject all python modules in a directory
# `--auto-inject` is going to find the auto-injection folder staring from
#                 the cwd. The name of the auto-injection folder is defaulted
#                 to `aga_injection`.


@test_case(20, 20, aga_expect=400, aga_expect_stdout="the result is 400\n", aga_value=5)
@test_case(10, 20, aga_expect=200, aga_value=5)
@prize(prize_fn, value=10.0, weight=0)
@problem()
def add(a: int, b: int) -> int:
    """Mul two numbers."""
    res = a * b
    print("the result is", res)
    return res


add.check()

# aga check injection_support.py --auto-inject
