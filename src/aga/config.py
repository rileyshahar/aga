"""Utilities for configuring `aga`."""

from dataclasses import MISSING, dataclass, field, fields
from importlib.resources import files
from typing import Any

import toml
from dacite import from_dict  # type: ignore


def _default_value(path: list[str]) -> Any:
    """Given a path of config names, get the value of the default at the leaf."""
    curr = _DEFAULT_CONFIG
    for val in path:
        curr = getattr(curr, val)

    return curr


def _from_default(path: list[str]) -> Any:
    """Given a path of config names, construct a field which inherits the default."""
    return field(default_factory=lambda: _default_value(path))  # type: ignore


@dataclass
class AgaTestConfig:
    """Aga's test-related configuration."""

    name_sep: str = _from_default(["test", "name_sep"])
    name_fmt: str = _from_default(["test", "name_fmt"])
    failure_msg: str = _from_default(["test", "failure_msg"])
    error_msg: str = _from_default(["test", "error_msg"])
    stdout_differ_msg: str = _from_default(["test", "stdout_differ_msg"])
    diff_explanation_msg: str = _from_default(["test", "diff_explanation_msg"])

    def update_weak(self, other: "AgaTestConfig") -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)


@dataclass
class AgaLoaderConfig:
    """Aga's submission loading configuration."""

    # this is pretty gross, we should find an easier way to do this
    # we're doing this so we can single-source-of-truth the defaults in `defults.toml`.
    import_error_msg: str = _from_default(["loader", "import_error_msg"])
    no_match_msg: str = _from_default(["loader", "no_match_msg"])
    too_many_matches_msg: str = _from_default(["loader", "too_many_matches_msg"])
    no_script_error_msg: str = _from_default(["loader", "no_script_error_msg"])
    multiple_scripts_error_msg: str = _from_default(
        ["loader", "multiple_scripts_error_msg"]
    )

    def update_weak(self, other: "AgaSubmissionConfig") -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)


@dataclass
class AgaSubmissionConfig:
    """Aga's submission configuration."""

    failed_tests_msg: str = _from_default(["submission", "failed_tests_msg"])
    failed_hidden_tests_msg: str = _from_default(
        ["submission", "failed_hidden_tests_msg"]
    )
    no_failed_tests_msg: str = _from_default(["submission", "no_failed_tests_msg"])

    def update_weak(self, other: "AgaSubmissionConfig") -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)


@dataclass
class AgaProblemConfig:
    """Aga's problem-related configuration."""

    check_stdout: bool = _from_default(["problem", "check_stdout"])
    check_stdout_overridden: bool = False

    mock_input: bool = _from_default(["problem", "mock_input"])
    mock_input_overridden: bool = False

    def update_weak(self, other: "AgaProblemConfig") -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)


@dataclass
class AgaConfig:
    """Aga's configuration."""

    test: AgaTestConfig = field(default_factory=AgaTestConfig)
    submission: AgaSubmissionConfig = field(default_factory=AgaSubmissionConfig)
    loader: AgaLoaderConfig = field(default_factory=AgaLoaderConfig)
    problem: AgaProblemConfig = field(default_factory=AgaProblemConfig)

    def update_weak(self, other: "AgaConfig") -> None:
        """Update all default attributes of self to match other."""
        for attr in fields(self):
            getattr(self, attr.name).update_weak(getattr(other, attr.name))


def _update_weak_leaf(self, other) -> None:  # type: ignore
    """Update a leaf-level dataclass weakly."""
    # iterate over all the fields of the dataclass, checking them against the
    # default value, and updating them to the other value if they match the default
    # value
    for attr in fields(self):
        if (
            attr.default_factory != MISSING  # type: ignore
            # flake8: noqa
            and attr.default_factory() == getattr(self, attr.name)  # type: ignore
        ):
            try:
                if getattr(self, attr.name + "_overridden"):
                    continue
            except AttributeError:
                # if there is no overridden tracker, we assume it's safe to override
                pass

            setattr(self, attr.name, getattr(other, attr.name))


def load_config_from_path(path: str) -> AgaConfig:
    """Load the toml file at path."""
    return from_dict(  # type: ignore
        data_class=AgaConfig,
        data=toml.load(path),
    )


_DEFAULT_CONFIG: AgaConfig = load_config_from_path(
    # this is type safe, but there's not actually a safe way to indicate that to mypy,
    # since `Traversable` (the type returned by `joinpath`) isn't re-exported by
    # `importlib.resources`
    files("aga").joinpath("defaults.toml")  # type: ignore
)
