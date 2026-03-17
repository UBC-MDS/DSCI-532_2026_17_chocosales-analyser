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