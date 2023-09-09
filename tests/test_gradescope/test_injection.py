from __future__ import annotations

import pathlib
from types import ModuleType
from typing import Generator, Iterable
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from aga.config import INJECTION_MODULE_FLAG, AgaConfig


@pytest.fixture()
def fake_aga_config(
    injection_tear_down: Generator[None, None, None]
) -> Generator[AgaConfig, None, None]:
    yield AgaConfig()


file_dir = pathlib.Path(__file__).parent
resource_dir = file_dir / "resources"
auto_injection_dir = resource_dir / "aga_injection"


@pytest.fixture()
def mocked_find_injection_dir(mocker: MockerFixture) -> MagicMock:
    patched = mocker.patch("aga.config._find_injection_dir")
    patched.return_value = auto_injection_dir

    return patched


@pytest.mark.parametrize(
    "injected_files, injected_dirs, injection_module, auto_inject",
    [
        pytest.param(
            [
                resource_dir / "injection_file_1.py",
                resource_dir / "injection_file_2.py",
            ],
            [resource_dir / "injection_dir_1", resource_dir / "injection_dir_2"],
            "injection_module",
            False,
            id="test injection config with files and dirs",
        ),
        pytest.param(
            [
                resource_dir / "injection_file_1.py",
                resource_dir / "injection_file_2.py",
            ],
            [resource_dir / "injection_dir_1", resource_dir / "injection_dir_2"],
            "injection_module_different",
            False,
            id="test different injection module name",
        ),
        pytest.param([], [], "injection_module", False, id="no injection content"),
        pytest.param(
            [
                resource_dir / "injection_file_1.py",
                resource_dir / "injection_file_2.py",
            ],
            [resource_dir / "injection_dir_1", resource_dir / "injection_dir_2"],
            "injection_module_diff",
            True,
            id="test auto injection",
        ),
    ],
)
def test_injection_config(
    fake_aga_config: AgaConfig,
    mocked_find_injection_dir: MagicMock,
    injected_files: Iterable[pathlib.Path],
    injected_dirs: Iterable[pathlib.Path],
    injection_module: str,
    auto_inject: bool,
) -> None:
    """Test that the injection config is valid."""
    from aga.cli.app import _load_injection_config

    _load_injection_config(
        fake_aga_config,
        injected_files,
        injected_dirs,
        injection_module,
        auto_inject,
    )

    injection_config = fake_aga_config.injection

    assert all(file in injection_config.inject_files for file in injected_files)
    assert all(dir_ in injection_config.inject_dirs for dir_ in injected_dirs)
    assert injection_config.injection_module
    assert injection_config.injection_module.__name__ == f"aga.{injection_module}"
    assert getattr(injection_config.injection_module, INJECTION_MODULE_FLAG)
    assert auto_injection_dir in injection_config.inject_dirs if auto_inject else True


def test_bad_injection_config(
    fake_aga_config: AgaConfig,
    mocked_find_injection_dir: MagicMock,
) -> None:
    """Test that the injection config is valid."""
    from aga.cli.app import _load_injection_config

    with pytest.raises(ValueError, match="injection files or dirs are invalid"):
        _load_injection_config(
            fake_aga_config,
            [pathlib.Path("not_exist.py")],
            [],
            "injection",
            False,
        )

        with pytest.raises(ValueError, match="injection files or dirs are invalid"):
            _load_injection_config(
                fake_aga_config,
                [],
                [pathlib.Path("not_exist/")],
                "injection",
                False,
            )


def test_find_injection() -> None:
    from aga.config import _find_injection_dir

    assert _find_injection_dir("resources", file_dir)
    assert _find_injection_dir("aga_injection", resource_dir)


def test_injecting_from_files() -> None:
    from aga.config import _inject_from_file

    temp_module = ModuleType("aga.temp_module")
    _inject_from_file(temp_module, auto_injection_dir / "mock_injection.py")

    temp_dir = dir(temp_module)
    assert "prize_fn" in temp_dir
    assert "_prize_fn_hidden" not in temp_dir
    assert "value" in temp_dir
    assert "_value_hidden" not in temp_dir
    assert "PrizeClass" in temp_dir
    assert "_PrizeClassHidden" not in temp_dir


def test_duplicated_injection(injection_tear_down: None) -> None:
    import aga
    from aga.cli.app import _load_injection_config

    _load_injection_config(
        AgaConfig(),
        [],
        [],
        "injection_module",
        False,
    )

    assert "injection_module" in dir(aga)

    with pytest.raises(ValueError):
        _load_injection_config(
            AgaConfig(),
            [],
            [],
            "injection_module",
            False,
        )


def test_target_folder_not_exist() -> None:
    from aga.config import _find_injection_dir

    with pytest.raises(ValueError, match="No injection directory found."):
        _find_injection_dir("not_exist", file_dir)


def test_target_folder_is_not_dir() -> None:
    from aga.config import _find_injection_dir

    with pytest.raises(ValueError, match="is not a directory"):
        _find_injection_dir("test_injection.py", file_dir)
