"""mock file for testing injection."""


def prize_fn() -> str:  # pragma: no cover
    """Mock visible function."""
    return "prize"


def _hidden_prize_fn() -> str:  # pragma: no cover
    """Mock hidden function."""
    return "hidden_prize"


value = 10
_hidden_value = 20


class PrizeClass:
    """Mock visible class."""

    pass


class _PrizeClassHidden:
    """Mock hidden class."""

    pass
