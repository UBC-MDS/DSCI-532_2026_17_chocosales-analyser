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
    
