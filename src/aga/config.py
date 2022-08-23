"""Utilities for configuring `aga`."""

from dataclasses import dataclass, field, fields
from importlib.resources import files

import toml
from dacite import from_dict  # type: ignore


@dataclass
class AgaTestConfig:
    """Aga's test-related configuration."""

    name_sep: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.name_sep)
    name_fmt: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.name_fmt)
    failure_msg: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.failure_msg)
    error_msg: str = field(default_factory=lambda: _DEFAULT_CONFIG.test.error_msg)
    stdout_differ_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.test.stdout_differ_msg
    )
    diff_explanation_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.test.diff_explanation_msg
    )

    def update_weak(self, other: "AgaTestConfig") -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)


@dataclass
class AgaSubmissionConfig:
    """Aga's student submission-related configuration."""

    # this is pretty gross, we should find an easier way to do this
    # we're doing this so we can single-source-of-truth the defaults in `defults.toml`.
    import_error_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.submission.import_error_msg
    )
    no_match_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.submission.no_match_msg
    )
    too_many_matches_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.submission.too_many_matches_msg
    )
    failed_tests_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.submission.failed_tests_msg
    )
    failed_hidden_tests_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.submission.failed_hidden_tests_msg
    )
    no_failed_tests_msg: str = field(
        default_factory=lambda: _DEFAULT_CONFIG.submission.no_failed_tests_msg
    )

    def update_weak(self, other: "AgaSubmissionConfig") -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)


@dataclass
class AgaProblemConfig:
    """Aga's problem-related configuration."""

    check_stdout: bool = field(
        default_factory=lambda: _DEFAULT_CONFIG.problem.check_stdout
    )

    def update_weak(self, other: "AgaProblemConfig") -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)


@dataclass
class AgaConfig:
    """Aga's configuration."""

    test: AgaTestConfig = field(default_factory=AgaTestConfig)
    submission: AgaSubmissionConfig = field(default_factory=AgaSubmissionConfig)
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
        if attr.default_factory() == getattr(self, attr.name):  # type: ignore
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
