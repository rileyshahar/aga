# Injection 

## What is injection and why? 

Users of `aga` find they need to copy and paste snippets of scripts to each of problem description python file, which is creating a lot of redundant code. Take the following example. The `prize_fn` has to be copied every time a new problem is created. 

```python
def prize_fn(tests: list[TcOutput], _: SubmissionMetadata) -> tuple[float, str]:
    """Check that all tests passed."""
    # HUNDREDS OF LINES OF CODE HERE !!!!!
    if all(t.is_correct() for t in tests):
        return 1.0, "Good work! You earned these points since all tests passed."
    else:
        return 0.0, "To earn these points, make sure all tests pass."


@prize(prize_fn, value=10)
@problem()
def add(x: int, y: int) -> int:
    """Add x and y."""
    return x + y
```

To solve this problem, we introduce the concept of injection, so that the shared code can be written in one place and be injected in every problem description file. So that the code above can be rewritten as follows, and no duplicated code will be generated. 

```python
# shared_prize_func.py

def prize_fn(tests: list[TcOutput], _: SubmissionMetadata) -> tuple[float, str]:
    """Check that all tests passed."""
    # HUNDREDS OF LINES OF CODE HERE !!!!!
    if all(t.is_correct() for t in tests):
        return 1.0, "Good work! You earned these points since all tests passed."
    else:
        return 0.0, "To earn these points, make sure all tests pass."
```

```python
# problem 1
# ... necessary imports
from aga.injection import prize_fn


@prize(prize_fn, value=10)
@problem()
def add(x: int, y: int) -> int:
    """Add x and y."""
    return x + y
```

```python
# problem 2
# ... necessary imports
from aga.injection import prize_fn

@prize(prize_fn, value=10)
@problem()
def multiply(x: int, y: int) -> int:
    """Multiply x and y."""
    return x * y
```

## How to use injection

There are several commands related to injection. You can find the help and description in the CLI help message. It's duplicated down below for the convenience of reading.

```text
 --inject                    PATH  Inject a util file into the submission directory.
 --inject-all                PATH  Inject all util files in the specified folder into the submission directory.
 --injection-module          TEXT  The name of the module to import from the injection directory. [default: injection]
 --auto-inject                     Find the first injection directory recursively and automatically. 
```

You can specify a specific file to inject using `--inject <file_path>` or inject all files in a folder using `--inject-all <dir_path>`. You can also specify the name of the injection module, which is defaulted to `injection` so that the injection imports will be `from aga.injection import ...`. When changed to `my_injection` for example, it will make the import command to be `from aga.my_injection import ...`.

You can also use the `--auto-inject` flag to automatically find ___the first injection directory___ (this will likely be changed to ___all injection directories___ in the future) upward recursively. `aga` finds `aga_injection` folder starting from the current working directory, which is the folder in which you entered `aga gen/check/run` commands. For example, considering the following dir tree: 

```text
.
└── courses/
    └── csci121/
        ├── hw1/
        │   ├── aga_injection/
        │   │   └── jims_prize_fn.py
        │   └── pb1.py
        ├── hw2/
        │   ├── aga_injection/
        │   │   └── jams_prize_fn.py
        │   └── pb2.py
        └── aga_injection/
            └── jems_prize_fn.py
```

If `aga check --auto-inject pb1.py` is run in `hw1` directory, `jims_prize_fn.py` will be used. However, if `aga check --auto-inject ./hw1/pb1.py` is run in the `csci121` directory, `jems_prize_fn.py` will be used.
