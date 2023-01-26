"""Test the package metadata."""

from aga import __version__ as agaversion


def test_version() -> None:
    """Test that the version is correct."""
    assert agaversion == "0.12.1"
