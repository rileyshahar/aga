"""Utility classes for the core module."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Type, Sequence, Dict

__all__ = (
    "CaptureOut",
    "MethodCaller",
    "MethodCallerFactory",
    "PropertyGetter",
    "PropertyGetterFactory",
    "Initializer",
    "initializer",
)


def _ensure_formatting_dot(s: str) -> str:
    """Ensure that a string ends with a dot."""
    if s[0] != ".":
        return "." + s
    return s


class CaptureOut:
    """Context manager for capturing stdout."""

    def __init__(self, capture: bool):
        """Initialize the context manager."""
        self.capture: bool = capture
        self.capture_device: redirect_stdout[StringIO] | None = None
        self.io_device: StringIO | None = None

    def __enter__(self) -> CaptureOut:
        """Enter the context manager."""
        if self.capture:
            self.io_device = StringIO()
            self.capture_device = redirect_stdout(self.io_device)
            self.capture_device.__enter__()
        return self

    def __exit__(self, *args: Any) -> Any:
        """Exit the context manager."""
        if self.capture and self.capture_device:
            return self.capture_device.__exit__(*args)
        return None

    @property
    def value(self) -> str | None:
        """Return the captured output, or None if not capturing."""
        if self.capture and self.io_device:
            return self.io_device.getvalue()
        else:
            return None


# pylint: disable=too-few-public-methods
class MethodCaller:
    """Call a method on an instance."""

    def __init__(self, attr_name: str, *args: Any, **kwargs: Any):
        self._attr_name = attr_name
        self._args = args
        self._kwargs = kwargs

    @property
    def attr_name(self) -> str:
        """Return the method attribute name."""
        return self._attr_name

    @property
    def args(self) -> Sequence[Any]:
        """Return the positional arguments."""
        return self._args

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Return the keyword arguments."""
        return self._kwargs

    def __call__(self, instance: Any, previous_result: Any = None) -> Any:
        """Call the method on the instance."""
        return getattr(instance, self.attr_name)(*self.args, **self.kwargs)

    def __str__(self) -> str:
        """Return a string representation of the method call."""
        arg_repr = f'{", ".join(map(repr, self.args))}, ' if self.args else ""
        kwargs = (f"{k}={repr(v)}" for k, v in self.kwargs.items())  # type: ignore
        kwargs_repr = f'{", ".join(kwargs)}, ' if self.kwargs else ""
        return _ensure_formatting_dot(f"{self.attr_name}({arg_repr}{kwargs_repr})")

    def __repr__(self) -> str:
        """Return a string representation of the method call."""
        return self.__str__()


class MethodCallerFactory:
    """Factory for creating MethodCaller instances."""

    def __init__(self, attr_name: str):
        self._attr_name = attr_name

    @property
    def attr_name(self) -> str:
        """Return the method attribute name."""
        return self._attr_name

    def __call__(
        self, *args: Any, caller_class: Type[MethodCaller] = MethodCaller, **kwargs: Any
    ) -> MethodCaller:
        """Create a MethodCaller instance with the method name."""
        return caller_class(self._attr_name, *args, **kwargs)


# pylint: disable=too-few-public-methods
class PropertyGetter:
    """Get an attribute from an instance."""

    def __init__(self, *args: str) -> None:
        self._attr_names = args

    @property
    def attr_names(self) -> Sequence[str]:
        """Return the attribute name."""
        return self._attr_names

    def __str__(self) -> str:
        """Return a string representation of the property getter."""
        return _ensure_formatting_dot(
            ".".join(
                name[1:] if name.startswith(".") else name for name in self.attr_names
            )
        )

    def __repr__(self) -> str:
        """Return a string representation of the property getter."""
        return self.__str__()

    def __call__(self, instance: Any, previous_result: Any = None) -> Any:
        """Get the attribute from the instance."""
        if len(self.attr_names) == 0:
            raise ValueError("No properties specified in PropertyGetter")

        for i, attr_name in enumerate(self.attr_names):
            properties = attr_name.split(".")

            if properties[0] == "":
                properties = properties[1:]

            if len(properties) == 0:
                raise ValueError(
                    f"No properties specified in the {i}th attribute "
                    f"name in the PropertyGetter. "
                    f"All attributes specified: {self.attr_names}"
                )

            for property_name in properties:
                if property_name == "":
                    raise ValueError(f"Double . in {self.attr_names}")
                instance = getattr(instance, property_name)

        return instance


class PropertyGetterFactory:
    """Factory for creating PropertyGetter instances."""

    def __call__(
        self,
        *args: Any,
        getter_class: Type[PropertyGetter] = PropertyGetter,
        **kwargs: Any,
    ) -> PropertyGetter:
        """Create a PropertyGetter instance with the attribute name."""
        return getter_class(*args, **kwargs)


# pylint: disable=too-few-public-methods
class Initializer(MethodCaller):
    """Call the __init__ method on an instance."""

    DEFAULT_NEW_INSTANCE_NAME = "instance"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__("__call__", *args, **kwargs)


initializer = Initializer()
