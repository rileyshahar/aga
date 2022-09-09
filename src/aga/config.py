"""Utilities for configuring `aga`."""
from __future__ import annotations

import importlib.util
import pathlib
from dataclasses import MISSING, dataclass, field, fields
from importlib.resources import files
from types import ModuleType
from typing import Any, Set, Optional, Iterable

import toml
from dacite import from_dict, Config  # type: ignore


def _default_value(path: list[str]) -> Any:
    """Given a path of config names, get the value of the default at the leaf."""
    curr = _DEFAULT_CONFIG
    for val in path:
        curr = getattr(curr, val)

    return curr


def _from_default(path: list[str]) -> Any:
    """Given a path of config names, construct a field which inherits the default."""
    return field(default_factory=lambda: _default_value(path))  # type: ignore


def _grab_user_defined_properties(module: ModuleType) -> Set[str]:
    """Grab all the properties defined in the module."""
    return {name for name in dir(module) if not name.startswith("_")}


INJECTION_MODULE_FLAG = "__aga_injection_module__"


def _create_injection_module(module_name: str = "injection") -> ModuleType:
    import aga  # pylint: disable=import-outside-toplevel, cyclic-import
    import sys  # pylint: disable=import-outside-toplevel

    module_full_name = f"aga.{module_name}"

    if hasattr(aga, module_name) or module_full_name in sys.modules:
        raise ValueError(f'Module "{module_full_name}" already exists.')

    new_module = ModuleType(module_full_name)
    setattr(new_module, INJECTION_MODULE_FLAG, True)
    setattr(aga, module_name, new_module)

    sys.modules[module_full_name] = new_module

    return new_module


def _inject_from_file(module: Optional[ModuleType], file_path: pathlib.Path) -> None:
    if not module:
        raise ValueError("No module to inject into.")

    spec = importlib.util.spec_from_file_location(file_path.name, file_path)
    if not spec:
        raise ValueError(f"Unable to load file {file_path} for injection")

    temp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(temp_module)  # type: ignore
    wanted_properties = _grab_user_defined_properties(temp_module)

    for wanted_property in wanted_properties:
        setattr(module, wanted_property, getattr(temp_module, wanted_property))


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


def _find_injection_dir(
    injection_dir: str, starting_dir: Optional[pathlib.Path] = None
) -> pathlib.Path:
    """Find the injection directory."""
    target_folder = current_path = starting_dir or pathlib.Path.cwd()

    # sort of wrong, but it's ok, who will make a folder in the root
    while current_path != current_path.parent:
        if (target_folder := current_path / injection_dir).exists():
            break

        current_path = current_path.parent

    if not target_folder.exists():
        raise ValueError(
            "No injection directory found. It's likely to be an config error. "
        )

    if not target_folder.is_dir():
        raise ValueError(f"Injection directory ({target_folder}) is not a directory")

    return target_folder


@dataclass
class AgaInjectionConfig:
    """Aga's injection-related configuration."""

    inject_files: Set[pathlib.Path] = field(default_factory=set)
    inject_dirs: Set[pathlib.Path] = field(default_factory=set)
    injection_module: Optional[ModuleType] = field(default=None)
    auto_injection_folder: str = field(default="aga_injection")

    @property
    def is_valid(self) -> bool:
        """Whether this config is valid.

        inject files must but files
        inject dirs must be directories
        """
        return all(
            file.exists() and file.is_file() for file in self.inject_files
        ) and all(file.exists() and file.is_dir() for file in self.inject_dirs)

    def inject(self, module: Optional[ModuleType] = None) -> None:
        """Inject the specified files and those in dirs into the module."""
        module = module or self.injection_module

        for file_path in self.inject_files:
            _inject_from_file(module, file_path)

        for dir_path in self.inject_dirs:
            for file_path in dir_path.iterdir():
                if file_path.is_file() and file_path.suffix == ".py":
                    _inject_from_file(module, file_path)

    def create_injection_module(self, module_name: str) -> ModuleType:
        """Create a new module to inject into."""
        if not self.injection_module:
            self.injection_module = _create_injection_module(module_name)
        return self.injection_module

    def update_weak(self, other: AgaInjectionConfig) -> None:
        """Update all default attributes of self to match other."""
        _update_weak_leaf(self, other)

    def find_auto_injection(self) -> None:
        """Find the auto injection folder."""
        self.inject_dirs.add(_find_injection_dir(self.auto_injection_folder))

    def update(
        self, fls: Iterable[pathlib.Path] = (), dirs: Iterable[pathlib.Path] = ()
    ) -> None:
        """Update the injection config."""
        self.inject_files.update(fls)
        self.inject_dirs.update(dirs)


@dataclass
class AgaConfig:
    """Aga's configuration."""

    test: AgaTestConfig = field(default_factory=AgaTestConfig)
    submission: AgaSubmissionConfig = field(default_factory=AgaSubmissionConfig)
    loader: AgaLoaderConfig = field(default_factory=AgaLoaderConfig)
    problem: AgaProblemConfig = field(default_factory=AgaProblemConfig)
    injection: AgaInjectionConfig = field(default_factory=AgaInjectionConfig)

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
        config=Config(cast=[pathlib.Path, set]),
    )


_DEFAULT_CONFIG: AgaConfig = load_config_from_path(
    # this is type safe, but there's not actually a safe way to indicate that to mypy,
    # since `Traversable` (the type returned by `joinpath`) isn't re-exported by
    # `importlib.resources`
    files("aga").joinpath("defaults.toml")  # type: ignore
)
