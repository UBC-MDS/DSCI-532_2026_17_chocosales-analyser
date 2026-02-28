import pandas as pd
from typing import Union


def filter_sales(
    sales_df: pd.DataFrame,
    start_year: Union[int, str],
    end_year: Union[int, str],
    country: str = "All",
    product: str = "All",
) -> pd.DataFrame:
    """Filter sales transactions by year range and optional country/product.

    Expected columns in sales_df: year, country, product
    """
    start_year = int(start_year)
    end_year = int(end_year)

    year_min = min(start_year, end_year)
    year_max = max(start_year, end_year)

    filtered = sales_df[
        (sales_df["year"] >= year_min) & (sales_df["year"] <= year_max)
    ].copy()

    if country and country != "All":
        filtered = filtered[filtered["country"] == country].copy()

    if product and product != "All":
        filtered = filtered[filtered["product"] == product].copy()

    return filtered