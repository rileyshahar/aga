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

Now if we save this as `square.py`, we could run `aga gen square.py` in that
directory, which would generate a `problem.zip` file. However, we're not quite
done: we haven't given aga any test inputs yet! Let's do that:

```python
from aga import problem, test_case

@test_case(-2)
@test_case(2)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

Now re-run `aga gen square.py` and upload the resultant file to
[Gradescope](https://gradescope-autograders.readthedocs.io/en/latest/getting_started/).

There are a couple of things to know about this behavior.

First, there must be exactly one problem present in `square.py`. This is a
limitation that will hopefully be relaxed in the future.

Second, while the student can upload any number of files, precisely one of them
must contain a python object matching the name of the reference solution; in this
case, `square` (note that the reference solution object's name is used even if
another name is assigned to the problem itself via the `name` argument to the
decorator). Otherwise, the solution will be rejected. It's extremely important
to communicate this restriction to students.

Third, each test case will be run against the student's submission and the
golden solution. If the outputs differ, the test will be marked as failing. The
score of each test case will be half of the total score of the problem; by
default, each test case has equal weight. Modifying this default will be
discussed in
[Customizing Test Case Score](tutorial.html#customizing-test-case-score).

You can use a similar syntax for multiple arguments, or keyword arguments:

```python
@test_case(2, 1)  # defaults work as expected
@test_case(2, 1, sign=False)
@test_case(-3, 4, sign=False)
@problem()
def add_or_subtract(x: int, y: int, sign: bool = True) -> int:
    """If sign, add x and y; otherwise, subtract them."""
    if sign:
        return x + y
    else:
        return x - y
```

As a final note, you often won't want to upload the autograder to gradescope
just to see the output that's given to students. You can use the `aga run`
command to manually check a student submission in the command line.

## Testing the Golden Solution

We still have a single point of failure: the golden solution. _Golden tests_ are
aga's main tool for testing the golden solution. They work like simple unit tests;
you declare an input and expected output, which aga tests against your golden
solution. We expect that any cases you want to use to test your golden solution
will also be good test cases for student submissions, hence the following
syntax:

```python
@test_case(-2, aga_expect = 4)
@test_case(2, aga_expect = 4)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

Note that we prefix all keyword arguments to the `test_case` decorator with
`aga_`, so that you can still declare test inputs for problems with actual
keyword arguments.

`aga` can now check golden stdout now as well! Just add `aga_expect_stdout` to the test case(s). The format for the `aga_expect_stdout` is either a `str` or a `Iterable` of `str`. 

When a `str` is given, the given string will be checked against all the captured output. When an `Iterable` is given, the captured output string will be divided using `splitlines`, meaning each string in the `Iterable` should contain NO `\n` characters. 

The following examples will show. 

```python
@test_case(10, 20, aga_expect_stdout="the result is 30\n", aga_expect=30)
@problem()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    print("the result is", a + b)
    return a + b
```

```python
@test_case("Bob", aga_expect_stdout=["What is your name? ", "Hello, world! Bob!"])
@problem(script=True)
def hello_world() -> None:
    """Print 'Hello, world!'."""
    name = input("What is your name? ")
    print(f"Hello, world! {name}!")
```

If you run `aga check square`, it will run all golden tests (i.e., all test
cases with declared `aga_expect`), displaying any which fail. This also happens
by default when you run `aga gen square.py`, so you don't accidentally upload a
golden solution which fails unit testing.

## Customizing Test Case Score

By default, aga takes the problem's total score (configured on Gradescope) and
divides it evenly among each problem. This division is weighted by a parameter,
`aga_weight`, of `test_case`, which defaults to `1`. If our total score is 20,
and we want the `2` test case to be worth 15 and the `-2` to be worth 5, we can
do this:

```python
@test_case(-2, aga_expect = 4)
@test_case(2, aga_expect = 4, aga_weight = 3)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

It is also possible to directly control the value of test cases:

```python
@test_case(-2, aga_expect = 4)  # will get 100% of (total - 15) points
@test_case(2, aga_expect = 4, aga_weight = 0, aga_value = 15)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

However, this is not recommended, because it can lead to strange results if
there is incongruity between the values assigned via aga and the total score
assigned via Gradescope.

For complete semantics of score determination, see [Determining
Score](score.md).

## Generating Test Cases

You can check out `examples/inputs_for_test_cases.py` in the GitHub repo for more complete examples and comparisons.

If we want many test cases, we probably don't want to enumerate all of them by
hand. Aga therefore provides the [`test_cases`](reference.html#aga.test_cases)
decorator, which makes it easy to collect python generators (lists, `range`,
etc.) into test cases.

Let's start by testing an arbitrary set of inputs:

```python
from aga import problem, test_cases

@test_cases(-3, -2, 0, 1, 2, 100)
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

This will generate six test cases, one for each element in the list. Test cases
generated like this must share configuration, so while you can pass e.x.
`aga_weight` to the decorator, it will cause _each_ test case to have that
weight, rather than dividing the weight among the test cases.

The `@test_cases(-3, -2, 0, 1, 2, 100)` is equivalent to 

```python
from aga import param, test_cases, problem

@test_cases(param(-3), param(-2), param(0), param(1), param(2), param(100))
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

The directive `param` is used to wrap parameters to a function. Each `param` object is considered as a test case.

Similarly, we can generate tests for all inputs from -5 to 10:

```python
@test_cases(*range(-5, 11))
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

This will generate 16 test cases, one for each value in the range.

Or, we can generate tests programmatically, say from a file:

```python
from typing import Iterator

def inputs() -> Iterator[int]:
    with open("INPUTS.txt", "r", encoding="UTF-8") as f:
        for s in f.readlines():
            yield int(s.strip())

@test_cases(*inputs())
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

The generation happens when you run `aga gen` on your local machine, so you can
rely on resources (network, files, etc) not available in the Gradescope
environment.

### Multiple Arguments
#### Basics of Multiple Arguments
Say we want to generate inputs for multiple arguments (or keyword arguments),
e.x. for a difference function. We can use the natural syntax:

```python
@test_cases([(-3, 2), (-2, 1), (0, 0)], aga_params=True)
@problem()
def difference(x: int, y: int) -> int:
    """Compute x - y."""
    return x - y
```

There are four ways you can specify a batch of test cases: `params`, `zip` and `product`.

- `aga_params` will only take one iterable object, and each element in the iterable object will be unfolded when applied to the function. The example above will generate 3 tests, each to be `difference(-3, 2)`, `difference(-2, 1)` and `difference(0, 0)`. In the case where you want to add keyword arguments, you can use the `param` directive. 

    ```python
    from aga import problem, test_cases, param
    @test_cases([param(-3, y=2), param(-2, y=1), param(0, y=0)], aga_params=True)
    @problem()
    def difference(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y
    ```

    which is equivalent to

    ```python
    from aga import problem, test_cases, param
    @test_cases([(-3, 2), (-2, 1), (0, 0)], aga_params=True)
    @problem()
    def difference(x: int, y: int) -> int:
        """Compute x - y."""
        return x - y
    ```

- `<no-flag>` Note that this is different from the one above with `aga_params` flag. The example blow will generate 3 tests as well, but each to be `difference((-3, 2))`, `difference((-2, 1))` and `difference((0, 0))`.

```python
@test_cases((-3, 2), (-2, 1), (0, 0))
@problem()
def difference(tp) -> int:
    """Compute x - y."""
    x, y = tp
    return x - y
```

- `aga_singular_params` works similarly to `aga_params`. The following code is equivalent to `difference((-3, 2))`, `difference((-2, 1))` and `difference((0, 0))`. (Note that the `aga_params` flag is not needed.)

```python
from aga import problem, test_cases, param
@test_cases([(-3, 2), (-2, 1), (0, 0)], aga_singular_params=True)
@problem()
def difference(tp: Tuple[int, int]) -> int:
    """Compute x - y."""
    x, y = tp
    return x - y
```
  
It comes useful when you have a iterable of things where each single thing is going to serve as a parameter. 
    
```python
from aga import problem, test_cases, param
@test_cases(range(5), aga_singular_params=True)
@problem()
def square(x: int) -> int:
    """Compute x - y."""
    return x * x
```

The `@test_cases(range(5), aga_singular_params=True)` is equivalent to expanding the generator in the no flag version `@test_cases(*range(5))`. Note that `@test_cases(range(5), aga_params=True)` is not valid. 

- `aga_product` will take the cartesian product of all the arguments. In the above example, there will be 15 test cases, one for each combination of the arguments.

```python
@test_cases([-5, 0, 1, 3, 4], [-1, 0, 2], aga_product=True)
@problem()
def difference(x: int, y: int) -> int:
    """Compute x - y."""
    return x - y
```

- `aga_zip` will take the zip of all the arguments. In the example below, there will be 3 test cases, one for each pair of the arguments. This will short-circuit when the smaller iterator ends, so this will generate
three test cases: `(-5, -1)`, `(0, 0)`, and `(1, 2)`.

```python
@test_cases([-5, 0, 1, 3, 4], [-1, 0, 2], aga_zip=True)
@problem()
def difference(x: int, y: int) -> int:
    """Compute x - y."""
    return x - y
```

#### Shorthands 
You will find typing all the `aga_product` etc. to be tedious. In that case, you can use the shorthands provided. There are two ways you can write it simpler. 

- 
   ```python
   from aga import problem, test_cases
  
   @test_cases([-5, 0, 1, 3, 4], [-1, 0, 2])
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(...)
      ...

   @test_cases.params([-5, 0, 1, 3, 4], [-1, 0, 2])
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(..., aga_params=True)
      ...

   @test_cases.product([-5, 0, 1, 3, 4], [-1, 0, 2])
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(..., aga_product=True)
      ...

   @test_cases.zip([-5, 0, 1, 3, 4], [-1, 0, 2])
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(..., aga_zip=True)
      ...
  
   @test_cases.singular_params(([-5, 0, 1, 3, 4], [-1, 0, 2]))
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(..., aga_singular_params=True)
      ...
   ```

- 
   ```python
   from aga import problem, test_cases_params, test_cases_product, test_cases_zip

   @test_cases_params([-5, 0, 1, 3, 4], [-1, 0, 2])
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(..., aga_params=True)
      ...

   @test_cases_product([-5, 0, 1, 3, 4], [-1, 0, 2])
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(..., aga_product=True)
      ...

   @test_cases_zip([-5, 0, 1, 3, 4], [-1, 0, 2])
   @problem()
   def fn() -> None:
      # this is the same as @test_cases(..., aga_zip=True)
      ...
   ```

#### Note on `aga_*` keyword arguments
At this point, you might wonder what could be the input to `aga_*` keyword arguments. The good news is that you can do both singletons or iterables. When singleton is given, `aga` will match the number with the number of test cases. When an iterable is given, the number of elements must match the number of test cases and `aga` will check that. 

Foe example, if you want to set a series of tests to hidden and define a bunch of golden outputs for them, we can do 

```python
@test_cases([1, 2, 3], aga_hidden=True, aga_expect=[1, 4, 9])
@problem()
def square(x: int) -> int:
    """Square x."""
    return x * x
```

`@test_cases(1, 2, 3, aga_expect=[1, 1, 4, 4, 9, 9])` since the numbers don't match. 

## Checking Scripts

Sometimes, submissions look like python scripts, meant to be run from the
command-line, as opposed to importable libraries. To test a script, provide the
`script=True` argument to the `problem` decorator:

```python
@test_case("Alice", "Bob")
@test_case("world", "me")
@problem(script=True)
def hello_name() -> None:
    """A simple interactive script."""
    listener = input("Listener? ")
    print(f"Hello, {listener}.")

    speaker = input("Speaker ?")
    print(f"I'm {speaker}.")
```

This has three implications:

1. Aga will load the student submission as a script, instead of looking for a
   function with a matching name.
2. Aga will compare the standard output of the student submission to the
   standard output of the golden solution.
3. Aga will interpret the arguments to `test_case` as mocked outputs of the
   built in `input()` function. For example, for the "Alice","Bob" test case,
   aga will expect this standard output:

```
Hello, Alice.
I'm Bob.
```

## Creating Pipelines 

When testing against a class or an object, you can create a pipeline of functions to be called. This is useful if you want to test on the same object using different a sequence of actions. 

A pipeline is a sequence of function (which sometimes is referred as a process) that accepts two inputs, the object it's testing on and the previous result generated by the proceeding function, and outputs a result. The pipeline will be run on the golden solution and students' solution, and the output results will be compared individually. You can create a pipeline from any of the following directives. 

```python
from aga import test_case, param, test_cases, problem
from aga.core.utils import initializer

def fn1(obj, previous_result):
    ...

def fn2(obj, previous_result):
    ...

@test_case.pipeline(initializer, fn1, fn2)
@test_cases(param.pipeline(initializer, fn1, fn2))
@problem()
class TestProblem:
    ...
```

The library provides several useful functions. They can be imported from `aga.core.utils`, like the `initializer` function above. One can use `initializer` to initialize the class under testing. Note that if you want to initialize the class with arguments, you can *ONLY* use `initializer`. 

You can use the following linked list code as an example. It will generate a test case of multiple actions and outputs.

```python
from __future__ import annotations
from aga import test_case, problem
from aga.core.utils import initializer, MethodCallerFactory, PropertyGetterFactory

prepend = MethodCallerFactory("prepend")
display = MethodCallerFactory("display")
pop = MethodCallerFactory("pop")
get_prop = PropertyGetterFactory()

actions_and_outputs = {
    initializer: None,
    prepend(10): None,
    display(): None,
    prepend(20): None,
    display(): None,
    prepend(30): None,
    display(): None,
    get_prop("first.value"): 30,
    get_prop("first", "next", "value"): 20,
    get_prop("first", ".next", ".value"): 20,
    get_prop(".first", "next", "value"): 20,
    pop(): 30,
    pop(): 20,
    pop(): 10,
}


class Node:
    """A node in a linked list."""

    def __init__(self, value: int, next_node: Node | None = None) -> None:
        self.value = value
        self.next = next_node


@test_case.pipeline(
    *actions_and_outputs.keys(),
    aga_expect_stdout="< 10 >\n< 20 10 >\n< 30 20 10 >\n",
    aga_expect=list(actions_and_outputs.values()),
)
@problem()
class LL:
    """A linked list for testing."""

    def __init__(self) -> None:
        self.first: Node | None = None

    def __repr__(self) -> str:
        """Return a string representation of the list."""
        return f"< {self._chain_nodes(self.first)}>"

    def _chain_nodes(self, node: Node | None) -> str:
        if node is None:
            return ""
        else:
            return f"{node.value} {self._chain_nodes(node.next)}"

    def display(self) -> None:
        """Print the list."""
        print(self)

    def prepend(self, value: int) -> None:
        """Add a new element to the front of the list."""
        self.first = Node(value, self.first)

    def pop(self) -> int:
        """Remove the first element from the list and return it."""
        if self.first is None:
            raise IndexError("Cannot pop from an empty list")

        value = self.first.value
        self.first = self.first.next
        return value
```