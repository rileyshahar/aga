"""Utilities for aga."""
import difflib
from traceback import extract_tb


def text_diff(old: str, new: str) -> str:
    """Generate a diff between old and new."""
    old_list = old.splitlines(keepends=True)
    new_list = new.splitlines(keepends=True)

    return "".join(difflib.ndiff(old_list, new_list))


def limited_traceback(traceback) -> str:  # type: ignore
    """Format a traceback, including removing aga-specific parts of the trace."""
    # this is essentially a list of FrameSummary objects
    stack_summary = extract_tb(traceback)

    # this is a hack, but the idea is that if the file path has `aga` or `unittest` in
    # it, it's probably part of our infrastructure, rather than the student submission.
    out = ""
    for frame, formatted_frame in zip(stack_summary, stack_summary.format()):
        if "aga" in frame.filename or "unittest" in frame.filename:
            # reset output, we don't want any earlier lines bc student code hasn't been
            # called yet
            out = ""
        else:
            out += "\n"
            out += formatted_frame

    return out
