"""Tests for the configuration functionality."""

from aga.config import AgaConfig, AgaTestConfig


def test_example_defaults(default_config: AgaConfig) -> None:
    """Ensure that the example config has the correct defaults."""
    assert default_config == AgaConfig()


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
