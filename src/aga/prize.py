"""Add points prizes to problems.

This module contains the `prize` decorator, which lets you define custom post-test-run
points hooks for things like correctness and lateness. It also contains several prizes,
defined for convenience.
"""
from .core import SubmissionMetadata
from .runner import TcOutput
from .score import PrizeCriteria, all_correct, correct_and_on_time, on_time, prize

__all__ = (
    "prize",
    "all_correct",
    "on_time",
    "correct_and_on_time",
    "PrizeCriteria",
    "SubmissionMetadata",
    "TcOutput",
)
