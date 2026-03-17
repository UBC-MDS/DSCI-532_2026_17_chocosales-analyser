import re
from pathlib import Path

import pandas as pd
import pytest
from playwright.sync_api import Page, expect
from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

# Example run command:
# python -m pytest tests/test_app_playwright.py -v --browser firefox

APP_PATH = Path(__file__).resolve().parents[1] / "src" / "app.py"
app = create_app_fixture(str(APP_PATH))

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "chocolate_sales_clean.csv"
)

@pytest.fixture(scope="module")
def sales_df() -> pd.DataFrame:
    """Load cleaned data once for expected-value checks in UI tests."""
    df = pd.read_csv(DATA_PATH)
    if df["sales"].dtype == "object":
        df["sales"] = (
            df["sales"]
            .astype(str)
            .str.replace(r"[\$,]", "", regex=True)
            .astype(float)
        )
    return df

def _open_dashboard(page: Page, app_proc: ShinyAppProc) -> None:
    page.goto(app_proc.url)
    expect(
        page.get_by_text("Chocolate Sales Analyser Dashboard")
    ).to_be_visible()
    
def _set_filters(
    page: Page,
    *,
    start_year: int,
    end_year: int,
    country: str = "All",
    product: str = "All",
) -> None:
    page.locator("select#start_year").select_option(str(start_year))
    page.locator("select#end_year").select_option(str(end_year))
    page.locator("select#country").select_option(country)
    page.locator("select#product").select_option(product)

    controller.OutputText(page, "out_active_filter_state").expect_value(
        _expected_filter_state(
            start_year=start_year,
            end_year=end_year,
            country=country,
            product=product,
        )
    )
def _extract_total_revenue(page: Page) -> float:
    text = page.locator("body").inner_text()
    match = re.search(
        r"Total Sales Revenue\s*\(USD\)\s*\$([0-9,]+(?:\.[0-9]+)?)",
        text,
        re.S,
    )
    assert match is not None, "Could not parse Total Sales Revenue KPI."
    return float(match.group(1).replace(",", ""))

def _extract_total_transactions(page: Page) -> int:
    text = page.locator("body").inner_text()
    match = re.search(r"Total Transaction\s*\(Count\)\s*([0-9,]+)", text, re.S)
    assert match is not None, "Could not parse Total Transaction KPI."
    return int(match.group(1).replace(",", ""))

def _extract_yoy_main_text(page: Page) -> str:
    text = page.locator("body").inner_text()
    match = re.search(
        r"Year Over Year\s*Growth Rate\s*\(%\)\s*([0-9]+(?:\.[0-9]+)?%|N/A)",
        text,
        re.S,
    )
    assert match is not None, "Could not parse YoY main KPI text."
    return match.group(1)

#Aggregation Correctness behaviour tests verify that KPIs reflect the filtered dataset, which is critical for user trust.
def test_total_revenue_matches_filtered_aggregation(
    page: Page, app: ShinyAppProc, sales_df: pd.DataFrame
) -> None:
    """Verify total revenue equals filtered sums.

    This matters because KPIs must track active filters.
    """
    _open_dashboard(page, app)

    start_year = int(sales_df["year"].min())
    end_year = start_year + 1

    _set_filters(page, start_year=start_year, end_year=end_year)

    expected = float(
        sales_df[
            (sales_df["year"] >= start_year)
            & (sales_df["year"] <= end_year)
        ]["sales"].sum()
    )
    observed = _extract_total_revenue(page)

    assert observed == pytest.approx(expected, abs=0.1)
    
# Boundary Condition behaviour tests verify that edge cases yield correct outputs, which is critical for robustness and user confidence.
def test_yoy_boundary_same_start_and_end_year_is_zero(
    page: Page, app: ShinyAppProc, sales_df: pd.DataFrame
) -> None:
    """Verify start_year == end_year yields 0% YoY.

    This matters because equal periods imply no change.
    """
    _open_dashboard(page, app)

    year = int(sales_df["year"].min())
    _set_filters(page, start_year=year, end_year=year)

    assert _extract_yoy_main_text(page) == "0.0%"
    expect(page.get_by_text(f"{year} vs {year} (0%)")).to_be_visible()

# Edge-Case Filter behaviour tests verify that narrow filter combinations yield correct KPIs, which is important for filter consistency and user trust.
def test_country_product_year_slice_matches_expected_kpis(
    page: Page, app: ShinyAppProc, sales_df: pd.DataFrame
) -> None:
    """Verify a narrow year-country-product slice matches KPIs.

    This matters for filter consistency.
    """
    _open_dashboard(page, app)

    seed = sales_df.iloc[0]
    year = int(seed["year"])
    country = str(seed["country"])
    product = str(seed["product"])

    expected_slice = sales_df[
        (sales_df["year"] == year)
        & (sales_df["country"] == country)
        & (sales_df["product"] == product)
    ]
    expected_revenue = float(expected_slice["sales"].sum())
    expected_transactions = int(expected_slice.shape[0])

    _set_filters(
        page,
        start_year=year,
        end_year=year,
        country=country,
        product=product,
    )

    assert _extract_total_revenue(page) == pytest.approx(
        expected_revenue,
        abs=0.1,
    )
    assert _extract_total_transactions(page) == expected_transactions
    assert _extract_yoy_main_text(page) == "0.0%"
    expect(page.get_by_text(f"{year} vs {year} (0%)")).to_be_visible()