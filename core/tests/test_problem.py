"""Tests the for `problem` module."""

import pytest

from tests.square import square


def test_square() -> None:
    square.run_all_golden_tests()
