"""Tests for the configuration functionality."""

from aga import problem
from aga.config import AgaConfig, AgaProblemConfig, AgaTestConfig


def test_config_test_name(example_config: AgaConfig) -> None:
    """Check that the config test name is correct."""
    assert example_config.test.name_fmt == "Check with args {args} and kwargs {kwargs}."


def test_config_update_weak_default() -> None:
    """Test `update_weak` with a default field."""
    config1 = AgaConfig()
    config2 = AgaConfig(test=AgaTestConfig(name_fmt="other"))

    config1.update_weak(config2)

    assert config1.test.name_fmt == "other"


def test_config_update_weak_nondefault() -> None:
    """Test `update_weak` with a non-default field."""
    config1 = AgaConfig(test=AgaTestConfig(name_fmt="self"))
    config2 = AgaConfig(test=AgaTestConfig(name_fmt="other"))

    config1.update_weak(config2)

    assert config1.test.name_fmt == "self"


def test_config_overridden() -> None:
    """Test `update_weak` with a non-default field."""
    config = AgaConfig(problem=AgaProblemConfig(check_stdout=True, mock_input=False))

    @problem(check_stdout=False, mock_input=True)
    def dummy() -> None:  # pragma: no cover
        pass

    dummy.update_config_weak(config)

    # the problem decorator should override the config
    assert not dummy.config().problem.check_stdout
    assert dummy.config().problem.mock_input


def test_config_script() -> None:
    """Test that script defaults are overrideable."""

    @problem(script=True, check_stdout=False, mock_input=False)
    def dummy() -> None:  # pragma: no cover
        pass

    # the problem decorator should override the config
    assert not dummy.config().problem.check_stdout
    assert not dummy.config().problem.mock_input
