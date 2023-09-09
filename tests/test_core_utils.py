"""Test the aga.core.utils module."""

import pytest

from aga.core.utils import CaptureOut, MethodCallerFactory, PropertyGetterFactory


def test_capture_out() -> None:
    """Test the CaptureOut context manager."""
    with CaptureOut(True) as capture_out:
        print("hello")
    assert capture_out.value == "hello\n"

    with CaptureOut(False) as capture_out:
        print("world")
    assert capture_out.value is None


class DummyClass:
    """Dummy class for testing MethodCaller and PropertyGetter."""

    def __init__(self, value: int) -> None:
        self.value = value

    def add(self, x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    def sub(self, x: int, y: int) -> int:
        """Subtract two numbers."""
        return x - y


def test_method_caller() -> None:
    """Test the MethodCaller class."""
    obj = DummyClass(10)
    add_caller = MethodCallerFactory("add")
    assert add_caller.attr_name == "add"

    # Test calling a method with positional arguments
    adder = add_caller(1, 2)
    assert adder(obj) == 3

    # Test calling a method with keyword arguments
    adder = add_caller(x=3, y=4)
    assert adder(obj) == 7

    sub_caller = MethodCallerFactory("sub")
    # Test calling a different method on the same object
    suber = sub_caller(5, 2)
    assert suber(obj) == 3


def test_property_getter() -> None:
    """Test the PropertyGetter class."""
    obj = DummyClass(10)
    getter_factory = PropertyGetterFactory()

    # Test getting a single property
    getter = getter_factory("value")
    assert getter(obj) == 10

    # Test getting multiple properties
    getter = getter_factory(".add")
    assert getter(obj) == obj.add  # pylint: disable=comparison-with-callable

    # Test getting nested properties
    getter = getter_factory(".add.__name__")
    assert getter(obj) == "add"


def test_property_getter_errors() -> None:
    """Test the PropertyGetter class."""
    obj = DummyClass(10)
    getter_factory = PropertyGetterFactory()

    # Test getting non-existent property
    getter = getter_factory("non_existent_property")
    with pytest.raises(AttributeError, match="has no attribute "):
        getter(obj)

    # Test getting nested property with invalid attribute name
    getter = getter_factory(".add..non_existent_property")
    with pytest.raises(
        ValueError,
        match="Double . in",
    ):
        getter(obj)

    # Test getting property with empty attribute name
    getter = getter_factory("")
    with pytest.raises(
        ValueError, match="No properties specified in the 0th attribute "
    ):
        getter(obj)

    getter = getter_factory(".add", "", ".non_existent_property")
    with pytest.raises(
        ValueError, match="No properties specified in the 1th attribute "
    ):
        getter(obj)

    getter = getter_factory()
    with pytest.raises(ValueError, match="No properties specified in PropertyGetter"):
        getter(obj)


def test_str_repr_method_caller() -> None:
    """Test the __str__ and __repr__ methods of MethodCaller."""
    add_caller = MethodCallerFactory("add")
    adder = add_caller(1, 2)
    assert str(adder) == ".add(1, 2, )" == repr(adder)

    adder = add_caller(x=3, y=4)
    assert str(adder) == ".add(x=3, y=4, )" == repr(adder)

    adder = add_caller(1, 2, x=3, y=4)
    assert str(adder) == ".add(1, 2, x=3, y=4, )" == repr(adder)


def test_str_repr_prop_getter() -> None:
    """Test the __str__ and __repr__ methods of PropertyGetter."""
    getter = PropertyGetterFactory()
    adder = getter(".add", ".sub")
    assert str(adder) == ".add.sub" == repr(adder)

    adder = getter(".add", "sub")
    assert str(adder) == ".add.sub" == repr(adder)

    adder = getter("add", ".sub")
    assert str(adder) == ".add.sub" == repr(adder)

    adder = getter("add", "sub")
    assert str(adder) == ".add.sub" == repr(adder)

    adder = getter("add.sub")
    assert str(adder) == ".add.sub" == repr(adder)

    adder = getter(".add.sub", "add")
    assert str(adder) == ".add.sub.add" == repr(adder)
