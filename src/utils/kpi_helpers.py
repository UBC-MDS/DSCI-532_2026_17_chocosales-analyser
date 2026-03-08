"""Helpers for formatting KPI delta text in dashboard tiles."""


def format_delta_detail(
    delta: float | None,
    prev_year: int,
    na_text: str = "vs pre year N/A",
) -> tuple[str, str]:
    """Format a delta metric for executive-style KPI tile display.

    Parameters
    ----------
    delta
        Ratio change value (e.g., 0.125 for +12.5%).
    prev_year
        Previous year label used in the comparison text.
    na_text
        Text to display when delta is unavailable.

    Returns
    -------
    tuple[str, str]
        A tuple containing:
        1. Human-readable comparison text with arrow indicators.
        2. Bootstrap class string for color/styling.
    """
    # Shared text styling for the small detail line shown under each KPI value.
    base_class = "small mt-1 text-center d-block text-nowrap"

    # If we can't compute the change, show a neutral fallback message.
    if delta is None:
        return na_text, f"{base_class} text-white-50"

    # Positive change: up arrow + green text.
    if delta > 0:
        return (
            f"vs {prev_year} ▲ {delta * 100:.1f}%",
            f"{base_class} text-success",
        )

    # Negative change: down arrow + red text.
    if delta < 0:
        return (
            f"vs {prev_year} ▼ {abs(delta) * 100:.1f}%",
            f"{base_class} text-danger",
        )

    # Exactly no change: keep it neutral.
    return f"vs {prev_year} 0%", f"{base_class} text-white-50"


def format_delta_detail_with_value(
    delta: float | None,
    prev_year: int,
    prev_value: float | int | None,
    value_prefix: str = "",
    current_year: int | None = None,
    current_value: float | int | None = None,
) -> tuple[str, str]:
    """Format KPI delta as 'current_year vs prev_year (trend %)' text."""
    # Same base style, with color appended per trend direction.
    base_class = "small mt-1 text-center d-block text-nowrap"

    # No comparison available if either the delta or previous value is missing.
    if delta is None or prev_value is None:
        return f"vs {prev_year} N/A", f"{base_class} text-white-50"

    # Use provided current_year when available; otherwise infer from prev_year.
    display_current_year = (
        current_year if current_year is not None else prev_year + 1
    )
    pct_text = f"{abs(delta) * 100:.1f}%"

    if delta > 0:
        return (
            f"{display_current_year} vs {prev_year} (▲ {pct_text})",
            f"{base_class} text-success",
        )

    if delta < 0:
        return (
            f"{display_current_year} vs {prev_year} (▼ {pct_text})",
            f"{base_class} text-danger",
        )

    return (
        f"{display_current_year} vs {prev_year} (0%)",
        f"{base_class} text-white-50",
    )


def format_yoy_tile(
    yoy_value: float | None,
    prev_year: int,
    prev_value: float | int | None,
    current_year: int | None = None,
    current_value: float | int | None = None,
    value_prefix: str = "",
) -> tuple[str, str, str, str]:
    """Format YoY KPI text and Bootstrap classes for tile display.

    Returns
    -------
    tuple[str, str, str, str]
        main_text, detail_text, detail_class, main_text_class
    """
    # If YoY itself is unavailable, keep both text and color neutral.
    if yoy_value is None:
        return (
            "N/A",
            f"vs {prev_year} N/A",
            "small mt-1 text-center d-block text-white-50 text-nowrap",
            "text-white-50",
        )

    # Reuse the shared formatter so all KPI cards speak the same language.
    detail_text, detail_class = format_delta_detail_with_value(
        delta=yoy_value,
        prev_year=prev_year,
        prev_value=prev_value,
        value_prefix=value_prefix,
        current_year=current_year,
        current_value=current_value,
    )

    # Main YoY number color mirrors the trend direction.
    if yoy_value > 0:
        main_text_class = "text-success"
    elif yoy_value < 0:
        main_text_class = "text-danger"
    else:
        main_text_class = "text-white-50"

    return (
        f"{yoy_value * 100:,.1f}%",
        detail_text,
        detail_class,
        main_text_class,
    )
