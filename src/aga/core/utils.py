"""Utility classes for the core module"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch


__all__ = ("CaptureOut", "MethodCaller", "MethodCallerFactory")


class CaptureOut:
    """Context manager for capturing stdout."""

    def __init__(self, capture: bool):
        """Initialize the context manager."""
        self.capture: bool = capture
        self.capture_device: patch = None
        self.io: StringIO | None = None

    def __enter__(self) -> CaptureOut:
        """Enter the context manager."""
        if self.capture:
            self.io = StringIO()
            self.capture_device = redirect_stdout(self.io)
            self.capture_device.__enter__()
        return self

    def __exit__(self, *args):
        """Exit the context manager."""
        if self.capture:
            return self.capture_device.__exit__(*args)

    @property
    def value(self) -> str | None:
        """Return the captured output, or None if not capturing."""
        if self.capture:
            return self.io.getvalue()
        else:
            return None


class MethodCaller:
    def __init__(self, attr_name: str, *args, **kwargs):
        self._attr_name = attr_name
        self._args = args
        self._kwargs = kwargs

    def __call__(self, instance):
        return getattr(instance, self._attr_name)(*self._args, **self._kwargs)


class MethodCallerFactory:
    def __init__(self, attr_name: str):
        self._attr_name = attr_name

    @property
    def attr_name(self) -> str:
        return self._attr_name

    def __call__(self, *args, **kwargs):
        return MethodCaller(self._attr_name, *args, **kwargs)
