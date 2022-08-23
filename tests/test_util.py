"""Tests for the util module."""

from aga.util import text_diff


def test_text_diff() -> None:
    """Test the ndiff."""
    old = "ac\nd"
    new = "bc\nd"
    diff = text_diff(old, new)
    assert diff == "- ac\n+ bc\n  d"
