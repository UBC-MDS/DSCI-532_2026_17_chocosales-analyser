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
    base_class = "small mt-1 text-center d-block text-nowrap"

    if delta is None:
        return na_text, f"{base_class} text-white-50"

    if delta > 0:
        return (
            f"vs pre year ▲ {delta * 100:.0f}%",
            f"{base_class} text-success",
        )

    if delta < 0:
        return (
            f"vs pre year ▼ {abs(delta) * 100:.0f}%",
            f"{base_class} text-danger",
        )

    return "vs pre year 0%", f"{base_class} text-white-50"


def format_delta_detail_with_value(
    delta: float | None,
    prev_year: int,
    prev_value: float | int | None,
    value_prefix: str = "",
) -> tuple[str, str]:
    """Format delta line as: vs {year}: ↑ {value} ({pct}%)."""
    base_class = "small mt-1 text-center d-block text-nowrap"

    if delta is None or prev_value is None:
        return "vs pre year N/A", f"{base_class} text-white-50"

    value_text = f"{value_prefix}{prev_value:,.2f}"
    pct_text = f"{abs(delta) * 100:.0f}%"

    if delta > 0:
        return (
            f"vs pre year ▲ {value_text} ({pct_text})",
            f"{base_class} text-success",
        )

    if delta < 0:
        return (
            f"vs pre year ▼ {value_text} ({pct_text})",
            f"{base_class} text-danger",
        )

    return (
        f"vs pre year {value_text} (0%)",
        f"{base_class} text-white-50",
    )


def format_yoy_tile(
    yoy_value: float | None,
    prev_year: int,
    prev_value: float | int | None,
) -> tuple[str, str, str, str]:
    """Format YoY KPI text and Bootstrap classes for tile display.

    Returns
    -------
    tuple[str, str, str, str]
        main_text, detail_text, detail_class, main_text_class
    """
    if yoy_value is None:
        return (
            "N/A",
            "vs pre year N/A",
            "small mt-1 text-center d-block text-white-50 text-nowrap",
            "text-white-50",
        )

    detail_text, detail_class = format_delta_detail_with_value(
        delta=yoy_value,
        prev_year=prev_year,
        prev_value=prev_value,
    )
    if yoy_value > 0:
        main_text_class = "text-success"
    elif yoy_value < 0:
        main_text_class = "text-danger"
    else:
        main_text_class = "text-white-50"

    return f"{yoy_value * 100:,.1f}%", detail_text, detail_class, main_text_class