"""Utilities for aga."""
from traceback import extract_tb


def limited_traceback(traceback) -> str:  # type: ignore
    """Format a traceback, including removing aga-specific parts of the trace."""
    # this is essentially a list of FrameSummary objects
    stack_summary = extract_tb(traceback)

    # this is a hack, but the idea is that if the file path has `aga` or `unittest` in
    # it, it's probably part of our infrastructure, rather than the student submission.
    out = ""
    for (frame, formatted_frame) in zip(stack_summary, stack_summary.format()):
        if "aga" in frame.filename or "unittest" in frame.filename:
            pass
        else:
            out += "\n"
            out += formatted_frame

    return out
