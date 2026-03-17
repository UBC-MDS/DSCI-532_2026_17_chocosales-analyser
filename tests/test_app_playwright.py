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