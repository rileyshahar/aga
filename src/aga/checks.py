"""Additional checks and filters for problems."""
import ast
import inspect
from functools import wraps
from io import StringIO
from typing import Any, Callable, Iterable, Optional, TypeVar, Union
from unittest import TestCase
from unittest.mock import patch

__all__ = ("with_captured_stdout", "Site", "Disallow")

Output = TypeVar("Output")

Site = tuple[str, int]


def with_captured_stdout(
    func: Callable[..., Output]
) -> Callable[..., tuple[str, Output]]:
    """Run func, returning its stdout and normal return value."""

    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> tuple[str, Any]:
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            func_out = func(*args, **kwargs)

        return stdout.getvalue(), func_out

    return inner


class Disallow:
    """A list of items to disallow in code.

    Attributes
    ----------
    functions : list[str]
        The names of functions which the student should not be able to call.
    binops : list[type]
        The types of binary operations wihch the student should not be able to use.
        E.x., to forbid floating-point division, use `ast.Div`. See
        `here <https://docs.python.org/3/library/ast.html#ast.BinOp>`_ for a list.
    nodes : list[type]
        The types of any ast nodes wihch the student should not be able to use.
        E.x., to forbid for loops, use `ast.For`. See
        `the docs <https://docs.python.org/3/library/ast.html#node-classes>`_ for a
        list.

    Examples
    --------
    To disallow the built-in `map` function: `Disallow(functions=["map"])`.

    To disallow the built-in `str.map` function: `Disallow(functions=["count"])`.
    Note that for class method names, you just use the name of the function.

    Note that there is no way to disallow `+=` without also disallowing `+` with this
    API.
    """

    def __init__(
        self,
        functions: Optional[list[str]] = None,
        binops: Optional[list[type]] = None,
        nodes: Optional[list[type]] = None,
    ):
        self._functions = functions or []
        self._binops = binops or []
        self._nodes = nodes or []

    def to_test(
        self,
    ) -> Callable[[TestCase, Callable[..., Output], Callable[..., Output]], None]:
        """Generate a test method suitable for `aga_override_test` of `test_case`.

        You can pass the output of this method directly to `aga_override_test`.

        You can also use the lower-level methods `search_on_object` or `search_on_src`
        if you want to generate your own error message.
        """

        def inner(
            case: TestCase,
            _: Callable[..., Output],
            student: Callable[..., Output],
        ) -> None:
            msg = ""
            for site in self.search_on_object(student):
                if msg == "":
                    msg = "Looks like use you used some disallowed constructs:\n"

                msg += f"  - {site[0]} on line {site[1]}\n"

            case.assertEqual(msg, "", msg)

        return inner

    def search_on_object(self, obj: Any) -> Iterable[Site]:
        """Search for disallowed AST objects in a python object."""
        yield from self.search_on_src(inspect.getsource(obj))

    def search_on_src(
        self,
        src: str,
    ) -> Iterable[Site]:
        """Search for disallowed AST objects in a source string."""
        # Walk through each AST node (with no guarantee of order)
        for node in ast.walk(ast.parse(src)):

            # handle function calls
            if self._functions != [] and isinstance(node, ast.Call):
                use = _check_function(node.func, self._functions)  # type: ignore
                if use is not None:
                    yield use

            # handle binops
            if self._binops != [] and isinstance(node, (ast.BinOp, ast.AugAssign)):
                use = _check_binop(node, self._binops)
                if use is not None:
                    yield use

            # handle other objects
            if self._nodes != []:
                use = _check_ast_node(node, self._nodes)
                if use is not None:
                    yield use


def _check_function(call: ast.Call, functions: list[str]) -> Optional[Site]:
    """Check whether call is in functions."""
    # get the function name
    name = None
    if isinstance(call, ast.Name):
        name = call.id
    elif isinstance(call, ast.Attribute):
        name = call.attr

    if name is not None and name in functions:
        return (name, call.lineno)

    return None


def _check_binop(
    op_node: Union[ast.BinOp, ast.AugAssign], binops: list[type]
) -> Optional[Site]:
    """Check whether the binop is disallowed."""
    binop = op_node.op
    if type(binop) in binops:
        name = type(binop).__name__
        return (name, op_node.lineno)

    return None


def _check_ast_node(node: Any, nodes: list[type]) -> Optional[Site]:
    """Check whether an arbitrary AST node is disallowed."""
    if type(node) in nodes:
        name = type(node).__name__
        return (name, node.lineno)

    return None
