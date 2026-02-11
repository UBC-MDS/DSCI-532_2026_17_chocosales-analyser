# src/download_data.py
# Download Chocolate Sales dataset via kagglehub and save to data/raw/
#
# Usage:
#   python src/download_data.py

import os
import pandas as pd
import kagglehub

DATASET_ID = "saidaminsaidaxmadov/chocolate-sales"
CSV_FILENAME = "Chocolate Sales (2).csv"

OUT_DIR = os.path.join("data", "raw")
OUT_PATH = os.path.join(OUT_DIR, "chocolate_sales.csv")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    # If file already exists, we can skip downloading (optional but nice for reproducibility)
    if os.path.exists(OUT_PATH):
        print(f"[SKIP] {OUT_PATH} already exists. Remove it if you want to re-download.")
        return

    print(f"Loading from Kaggle via kagglehub: {DATASET_ID} -> {CSV_FILENAME}")

    df = kagglehub.dataset_load(
        kagglehub.KaggleDatasetAdapter.PANDAS,
        DATASET_ID,
        CSV_FILENAME,
    )

    # Parse Date column consistently
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

    df.to_csv(OUT_PATH, index=False)

    print(f"[OK] Saved to {OUT_PATH}")
    print(f"[INFO] Rows: {len(df)} | Columns: {df.shape[1]}")


if __name__ == "__main__":
    main()
