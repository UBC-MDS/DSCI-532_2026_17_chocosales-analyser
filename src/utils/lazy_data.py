from pathlib import Path
import pandas as pd
import ibis
from ibis import _


PARQUET_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "chocolate_sales_clean.parquet"
)


def get_duckdb_connection():
    """
    Create and return an ibis DuckDB connection.
    """
    return ibis.duckdb.connect()


def get_sales_table():
    """
    Return an ibis lazy table backed by the parquet file.

    This does NOT load the full dataset into memory.
    It only creates a lazy table reference.
    """
    if not PARQUET_PATH.exists():
        raise FileNotFoundError(
            f"Parquet file not found: {PARQUET_PATH}. "
            "Run src/convert_to_parquet.py first."
        )

    con = get_duckdb_connection()
    table = con.read_parquet(str(PARQUET_PATH), table_name="chocolate_sales")
    return table

def get_filter_choices() -> pd.DataFrame:
    """
    Return distinct year/country/product values for building UI filter choices.

    This is still queried from parquet via DuckDB/ibis, but only pulls
    a small distinct subset into memory.
    """
    t = get_sales_table()

    expr = t.select("year", "country", "product").distinct()

    return expr.execute()

def filter_sales_lazy(
    start_year: int,
    end_year: int,
    country: str = "All",
    product: str = "All",
) -> pd.DataFrame:
    """
    Apply dashboard filters lazily in DuckDB/ibis first,
    then execute and return only matching rows as a pandas DataFrame.
    """
    t = get_sales_table()

    expr = t.filter(
        (_.year >= int(start_year)) & (_.year <= int(end_year))
    )

    if country != "All":
        expr = expr.filter(_.country == country)

    if product != "All":
        expr = expr.filter(_.product == product)

    return expr.execute()

def get_full_sales_df() -> pd.DataFrame:
    """
    Load the full processed dataset from parquet via ibis + DuckDB.
    This is used for QueryChat, which expects a pandas DataFrame.
    """
    t = get_sales_table()
    return t.execute()