from pathlib import Path
import sys
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.filter_sales import filter_sales

@pytest.fixture
def sample_sales_df():
    """Small sample sales table used to verify filtering logic."""
    return pd.DataFrame(
        {
            "year": [2021, 2022, 2022, 2023, 2024],
            "country": ["USA", "USA", "Canada", "Canada", "USA"],
            "product": ["Dark", "Milk", "Dark", "White", "Milk"],
            "sales": [100, 200, 150, 175, 250],
        }
    )


def test_filter_sales_year_range(sample_sales_df):
    """
    Verify that the function keeps only rows within the requested year range,
    because the dashboard year controls should limit the displayed data correctly.
    """
    result = filter_sales(sample_sales_df, start_year=2022, end_year=2023)

    assert set(result["year"]) == {2022, 2023}
    assert len(result) == 3


def test_filter_sales_reversed_input(sample_sales_df):
    """
    Verify that reversed start and end years still produce the correct range,
    because users should get consistent filtering even if the year inputs are swapped.
    """
    result = filter_sales(sample_sales_df, start_year=2024, end_year=2022)

    assert set(result["year"]) == {2022, 2023, 2024}
    assert len(result) == 4


def test_filter_sales_filters_by_country_and_product(sample_sales_df):
    """
    Verify that country and product filters narrow the dataset correctly,
    because dashboard dropdown selections must return the intended subset.
    """
    result = filter_sales(
        sample_sales_df,
        start_year=2021,
        end_year=2024,
        country="USA",
        product="Milk",
    )

    assert len(result) == 2
    assert (result["country"] == "USA").all()
    assert (result["product"] == "Milk").all()


def test_filter_sales_missing_col():
    """
    Verify that the function raises a keyerror when columns are missing,
    because the dashboard depends on a valid input schema to filter safely.
    """
    bad_df = pd.DataFrame(
        {
            "year": [2022, 2023],
            "country": ["USA", "Canada"],
            # product column intentionally missing
        }
    )

    with pytest.raises(KeyError):
        filter_sales(bad_df, start_year=2022, end_year=2023)
