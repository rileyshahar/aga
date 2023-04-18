"""Utility classes for the core module."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Type


__all__ = (
    "CaptureOut",
    "MethodCaller",
    "MethodCallerFactory",
    "initializer",
)


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

    def __call__(self, instance: Any, previous_result: Any = None) -> Any:
        """Call the method on the instance."""
        return getattr(instance, self._attr_name)(*self._args, **self._kwargs)


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
    ) -> Any:
        """Create a MethodCaller instance with the method name."""
        return caller_class(self._attr_name, *args, **kwargs)


# pylint: disable=too-few-public-methods
class PropertyGetter:
    """Get an attribute from an instance."""

    def __init__(self, attr_name: str, *_, **__):
        self._attr_name = attr_name

    def __call__(self, instance: Any, previous_result: Any = None):
        return getattr(instance, self._attr_name)


class PropertyGetterFactory:
    """Factory for creating PropertyGetter instances."""

    def __init__(self, attr_name: str):
        self._attr_name = attr_name

    @property
    def attr_name(self) -> str:
        """Return the property's name."""
        return self._attr_name

    def __call__(self, *args, getter_class: Type = PropertyGetter, **kwargs):
        """Create a PropertyGetter instance with the attribute name."""
        return getter_class(self._attr_name, *args, **kwargs)


# pylint: disable=too-few-public-methods
class Initializer(MethodCaller):
    """Call the __init__ method on an instance."""

    def __init__(self, *args, **kwargs):
        super().__init__("__call__", *args, **kwargs)


initializer = Initializer()
