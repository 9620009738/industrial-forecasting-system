from pathlib import Path
import pandas as pd


RAW_FILE = Path("data/raw/iip_328.xlsx")
PROCESSED_DIR = Path("data/processed")

BASELINE_START = "2012-04-01"
BASELINE_END = "2025-03-01"


MONTH_MAP = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def create_baseline_dataset():
    print("=" * 60)
    print("CREATING PAPER BASELINE DATASET")
    print("=" * 60)

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_FILE}"
        )

    df = pd.read_excel(RAW_FILE)

    print(f"\nRaw observations: {len(df)}")

    df["month_number"] = df["month"].map(MONTH_MAP)

    if df["month_number"].isna().any():
        invalid_months = df.loc[
            df["month_number"].isna(),
            "month"
        ].unique()

        raise ValueError(
            f"Unknown month values found: {invalid_months}"
        )

    df["date"] = pd.to_datetime(
        {
            "year": df["year"].astype(int),
            "month": df["month_number"].astype(int),
            "day": 1,
        }
    )

    df = df.sort_values("date").reset_index(drop=True)

    baseline = df[
        (df["date"] >= BASELINE_START)
        & (df["date"] <= BASELINE_END)
    ].copy()

    baseline = baseline[
        [
            "date",
            "year",
            "month",
            "index",
            "growth_rate",
        ]
    ]

    expected_rows = 156

    if len(baseline) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} observations, "
            f"but found {len(baseline)}."
        )

    duplicate_dates = baseline["date"].duplicated().sum()

    if duplicate_dates != 0:
        raise ValueError(
            f"Found {duplicate_dates} duplicate dates."
        )

    missing_index = baseline["index"].isna().sum()

    if missing_index != 0:
        raise ValueError(
            f"Found {missing_index} missing index values."
        )

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        PROCESSED_DIR /
        "iip_food_products_baseline_2012_2025.csv"
    )

    baseline.to_csv(
        output_file,
        index=False
    )

    print(f"\nBaseline observations: {len(baseline)}")

    print(
        f"Date range: "
        f"{baseline['date'].min().date()} → "
        f"{baseline['date'].max().date()}"
    )

    print(f"\nDuplicate dates: {duplicate_dates}")
    print(f"Missing index values: {missing_index}")

    print("\nFirst 5 observations:")
    print(baseline.head().to_string(index=False))

    print("\nLast 5 observations:")
    print(baseline.tail().to_string(index=False))

    print(f"\nSaved to:\n{output_file}")

    print("\n" + "=" * 60)
    print("BASELINE DATASET CREATED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    create_baseline_dataset()