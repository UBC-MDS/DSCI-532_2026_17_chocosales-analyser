from pathlib import Path
import pandas as pd


CSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "chocolate_sales_clean.csv"
)

PARQUET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "chocolate_sales_clean.parquet"
)


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Processed CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    # Keep a few key dtypes stable before writing parquet
    if "year" in df.columns:
        df["year"] = df["year"].astype(int)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # If sales is still stored as strings like "$1,200", clean once here
    if "sales" in df.columns and df["sales"].dtype == "object":
        try:
            df["sales"] = (
                df["sales"]
                .astype(str)
                .str.replace(r"[\$,]", "", regex=True)
                .astype(float)
            )
        except Exception:
            # Leave as-is if sales is already clean or not monetary text
            pass

    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_PATH, index=False)

    print(f"[OK] Wrote parquet file to: {PARQUET_PATH}")
    print(f"[INFO] Rows: {df.shape[0]} | Columns: {df.shape[1]}")


if __name__ == "__main__":
    main()