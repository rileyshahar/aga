from __future__ import annotations
from aga import test_case, problem
from aga.core.utils import initializer, MethodCallerFactory, PropertyGetterFactory

prepend = MethodCallerFactory("prepend")
display = MethodCallerFactory("display")
pop = MethodCallerFactory("pop")
get_prop = PropertyGetterFactory()


actions_and_results = {
    initializer: None,
    prepend(10): None,
    display(): None,
    prepend(20): None,
    display(): None,
    prepend(30): None,
    display(): None,
    get_prop("first.value"): 30,
    get_prop(".first", ".next", ".value"): 20,
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
    *actions_and_results.keys(),
    aga_expect_stdout="< 10 >\n< 20 10 >\n< 30 20 10 >\n",
    aga_expect=list(actions_and_results.values()),
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
