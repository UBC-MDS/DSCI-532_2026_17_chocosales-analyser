"""Helpers for formatting KPI delta text in dashboard tiles."""


def format_delta_detail(delta: float | None, prev_year: int) -> tuple[str, str]:
    """Format a delta metric for executive-style KPI tile display.

    Parameters
    ----------
    delta
        Ratio change value (e.g., 0.125 for +12.5%).
    prev_year
        Previous year label used in the comparison text.

    Returns
    -------
    tuple[str, str]
        A tuple containing:
        1. Human-readable comparison text with arrow indicators.
        2. Bootstrap class string for color/styling.
    """
    if delta is None:
        return "vs previous year: N/A", "small text-muted mt-1"

    if delta > 0:
        return (
            f"vs {prev_year}: ↑ {delta * 100:.1f}%",
            "small text-success mt-1",
        )

    if delta < 0:
        return (
            f"vs {prev_year}: ↓ {abs(delta) * 100:.1f}%",
            "small text-danger mt-1",
        )

    return f"vs {prev_year}: 0.0%", "small text-muted mt-1"
