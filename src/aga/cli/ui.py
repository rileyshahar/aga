"""The command-line UI."""

from rich import print as rprint
from rich.box import ROUNDED
from rich.panel import Panel

from ..runner import ProblemOutput

RICH_PANEL_OPTS = {
    "box": ROUNDED,
    "title_align": "left",
    "subtitle_align": "right",
}


def print_fancy_summary(output: ProblemOutput) -> None:
    """Print a fancy summary of the problem."""
    rprint(
        Panel(
            output.output,
            title="Overall",
            subtitle=f"Total score: {output.score}",
            **RICH_PANEL_OPTS,  # type: ignore
        )
    )

    for test in output.tests:
        rprint(
            Panel(
                test.rich_output,
                title=("" if test.is_correct() else "[bright_red]")
                + ("(HIDDEN) " if test.hidden else "")
                + test.name,
                subtitle=f"{test.score}/{test.max_score}",
                **RICH_PANEL_OPTS,  # type: ignore
            )
        )
