from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "sectors"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "iip_multi_sector_2012_2025.csv"
)


# ---------------------------------------------------------
# Sector file mapping
# ---------------------------------------------------------

SECTOR_FILES = {
    "Textiles": "iip_textiles.xlsx",
    "Chemicals and Chemical Products": "iip_chemicals.xlsx",
    "Basic Metals": "iip_basic_metals.xlsx",
    "Motor Vehicles": "iip_motor_vehicles.xlsx",
}


# ---------------------------------------------------------
# Month mapping
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Date range
# ---------------------------------------------------------

START_DATE = pd.Timestamp("2012-04-01")
END_DATE = pd.Timestamp("2025-03-01")


# ---------------------------------------------------------
# Process one sector
# ---------------------------------------------------------

def process_sector(sector_name, filename):

    file_path = RAW_DIR / filename

    print("\n" + "-" * 70)
    print(f"Processing: {sector_name}")
    print(f"File: {filename}")

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    df = pd.read_excel(file_path)

    # Check required columns
    required_columns = [
        "base_year",
        "year",
        "month",
        "type",
        "category",
        "sub_category",
        "index",
        "growth_rate",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{sector_name}: missing columns "
            f"{missing_columns}"
        )

    # Convert month names to month numbers
    df["month_number"] = df["month"].map(MONTH_MAP)

    if df["month_number"].isna().any():
        invalid_months = (
            df.loc[
                df["month_number"].isna(),
                "month"
            ]
            .unique()
        )

        raise ValueError(
            f"{sector_name}: invalid month values "
            f"{invalid_months}"
        )

    # Create date
    df["date"] = pd.to_datetime(
        {
            "year": df["year"].astype(int),
            "month": df["month_number"].astype(int),
            "day": 1,
        }
    )

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    # Restrict to research period
    df = df[
        (df["date"] >= START_DATE)
        & (df["date"] <= END_DATE)
    ].copy()

    # Add sector label
    df["sector"] = sector_name

    # Keep analytical columns
    df = df[
        [
            "date",
            "year",
            "month",
            "index",
            "growth_rate",
            "sector",
        ]
    ].copy()

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    expected_rows = 156

    if len(df) != expected_rows:
        raise ValueError(
            f"{sector_name}: expected "
            f"{expected_rows} rows, got {len(df)}"
        )

    if df["date"].duplicated().any():
        raise ValueError(
            f"{sector_name}: duplicate dates detected"
        )

    if df["index"].isna().any():
        raise ValueError(
            f"{sector_name}: missing index values detected"
        )

    if df["date"].min() != START_DATE:
        raise ValueError(
            f"{sector_name}: incorrect first date "
            f"{df['date'].min()}"
        )

    if df["date"].max() != END_DATE:
        raise ValueError(
            f"{sector_name}: incorrect last date "
            f"{df['date'].max()}"
        )

    print(f"Rows: {len(df)}")
    print(f"Date range: {df['date'].min().date()} "
          f"to {df['date'].max().date()}")
    print(f"Missing index values: "
          f"{df['index'].isna().sum()}")
    print(f"Duplicate dates: "
          f"{df['date'].duplicated().sum()}")
    print(f"Index min: {df['index'].min()}")
    print(f"Index max: {df['index'].max()}")

    return df


# ---------------------------------------------------------
# Process all sectors
# ---------------------------------------------------------

all_sector_data = []

for sector_name, filename in SECTOR_FILES.items():

    sector_df = process_sector(
        sector_name,
        filename
    )

    all_sector_data.append(sector_df)


# ---------------------------------------------------------
# Combine
# ---------------------------------------------------------

combined_df = pd.concat(
    all_sector_data,
    ignore_index=True
)

combined_df = combined_df.sort_values(
    ["sector", "date"]
).reset_index(drop=True)


# ---------------------------------------------------------
# Final validation
# ---------------------------------------------------------

expected_total_rows = (
    len(SECTOR_FILES) * 156
)

if len(combined_df) != expected_total_rows:
    raise ValueError(
        f"Expected {expected_total_rows} total rows, "
        f"got {len(combined_df)}"
    )

sector_counts = (
    combined_df["sector"]
    .value_counts()
)

print("\n" + "=" * 70)
print("MULTI-SECTOR VALIDATION")
print("=" * 70)

print(
    f"Total rows: {len(combined_df)}"
)

print(
    f"Number of sectors: "
    f"{combined_df['sector'].nunique()}"
)

print("\nRows per sector:")
print(sector_counts.sort_index())


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

combined_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)
print("MULTI-SECTOR CLEANING COMPLETED")
print("=" * 70)