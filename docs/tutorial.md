# Tutorial

## Preliminaries

Ensure the aga CLI is available in your environment (`which aga`) and updated
to the current version (`aga --version`). If not, you can install it with `pip`
or a tool like [`poetry`](https://github.com/python-poetry/poetry).

## Getting Started

We're going to write a simple autograder for a basic problem: implementing a
function to square an integer.

Whenever you write an aga autograder, you start by writing a reference
implementation, which aga calls the _golden solution_. The library is based on
the idea that reference implementations have uniquely beneficial properties for
autograding homework; see [motivation](index.html#motivation). So, here's our
implementation:

```python
def square(x: int) -> int:
    """Square x."""
    return x * x
```

The type annotations and docstring are just because they're good practice; as of
now, aga does nothing with them. You might put, for example, the text of the
problem that you're giving to students, so it's there for easy reference.

Now we need to tell aga to turn this into a problem. We do that with the
[`problem`](reference.html#aga.problem) decorator:

```python
from aga import problem

@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

Aga's API is based around decorators; if you're not familiar with them, I
suggest finding at least a brief introduction. `problem` will always be the
first decorator you apply to any golden solution.

Now if we save this as a `.py` file, we could run `aga gen square` in that
directory, which would generate a `problem.zip` file. Note that the name of the
source file which holds the problem doesn't matter; it's the name of the
problem, which defaults to just the name of the function, that aga looks for.
See [Problem Discovery](cli.html#problem-discovery) for more.

However, we're not quite done: we haven't given aga any test inputs yet! Let's
do that:

```python
from aga import problem, test_case

@test_case(-2)
@test_case(2)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

Now re-run `aga gen square` and upload the resultant file to
[Gradescope](https://gradescope-autograders.readthedocs.io/en/latest/getting_started/).

There are a couple of things to know about the behavior of this autograder.

First, while the student can upload any number of files, precisely one of them
must contain a python object matching the name of the reference solution; in this
case, `square` (note that the reference solution object's name is used even if
another name is assigned to the problem itself via the `name` argument to the
decorator). Otherwise, the solution will be rejected. It's extremely important
to communicate this restriction to students.

Second, each test case will be run against the student's submission and the
golden solution. If the outputs differ, the test will be marked as failing. The
score of each test case will be half of the total score of the problem; by
default, each test case has equal weight. Modifying this default will be
discussed in [Custom Weights](tutorial.html#custom-weights).

## Golden Tests

TODO

## Custom Weights

TODO
