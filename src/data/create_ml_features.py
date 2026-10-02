import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/iip_food_products_baseline_2012_2025.csv"
)

OUTPUT_FILE = Path(
    "data/processed/iip_food_products_ml_features.csv"
)


print("=" * 70)
print("ML FEATURE ENGINEERING — FOOD PRODUCTS IIP")
print("=" * 70)


# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

df = (
    df.sort_values("date")
    .reset_index(drop=True)
)


print("\nOriginal dataset:")
print(f"Rows: {len(df)}")
print(
    f"Date range: "
    f"{df['date'].min()} → {df['date'].max()}"
)


# ---------------------------------------------------------
# 2. Create time-based features
# ---------------------------------------------------------

df["month_number"] = df["date"].dt.month

df["quarter"] = df["date"].dt.quarter

df["year_number"] = df["date"].dt.year


# Cyclic encoding of month
#
# This represents the circular nature of months:
# December is close to January.
# ---------------------------------------------------------

import numpy as np

df["month_sin"] = np.sin(
    2 * np.pi * df["month_number"] / 12
)

df["month_cos"] = np.cos(
    2 * np.pi * df["month_number"] / 12
)


# ---------------------------------------------------------
# 3. Lag features
# ---------------------------------------------------------
#
# IMPORTANT:
# Every lag uses only historical IIP values.
#
# No future information is used.
# ---------------------------------------------------------

lag_periods = [1, 2, 3, 6, 12]

for lag in lag_periods:

    df[f"lag_{lag}"] = (
        df["index"].shift(lag)
    )


# ---------------------------------------------------------
# 4. Rolling features
# ---------------------------------------------------------
#
# IMPORTANT:
# Shift by one month before calculating rolling
# statistics.
#
# Therefore the current target value is never included
# in its own features.
# ---------------------------------------------------------

historical_index = df["index"].shift(1)

rolling_windows = [3, 6, 12]

for window in rolling_windows:

    df[f"rolling_mean_{window}"] = (
        historical_index
        .rolling(window=window)
        .mean()
    )

    df[f"rolling_std_{window}"] = (
        historical_index
        .rolling(window=window)
        .std()
    )


# ---------------------------------------------------------
# 5. Target
# ---------------------------------------------------------

df["target"] = df["index"]


# ---------------------------------------------------------
# 6. Feature columns
# ---------------------------------------------------------

feature_columns = [
    "month_number",
    "quarter",
    "year_number",
    "month_sin",
    "month_cos",

    "lag_1",
    "lag_2",
    "lag_3",
    "lag_6",
    "lag_12",

    "rolling_mean_3",
    "rolling_std_3",

    "rolling_mean_6",
    "rolling_std_6",

    "rolling_mean_12",
    "rolling_std_12",
]


# ---------------------------------------------------------
# 7. Remove rows without enough historical information
# ---------------------------------------------------------

ml_df = df[
    [
        "date",
        "target"
    ] + feature_columns
].copy()

before_drop = len(ml_df)

ml_df = ml_df.dropna().reset_index(drop=True)

after_drop = len(ml_df)


print("\nFeature dataset:")
print(f"Rows before removing NaN: {before_drop}")
print(f"Rows after removing NaN:  {after_drop}")

print(
    f"Date range after feature creation: "
    f"{ml_df['date'].min()} → {ml_df['date'].max()}"
)


# ---------------------------------------------------------
# 8. Feature list
# ---------------------------------------------------------

print("\nFeatures:")
for feature in feature_columns:
    print(f"  - {feature}")


# ---------------------------------------------------------
# 9. Missing-value check
# ---------------------------------------------------------

print("\nMissing values:")

print(
    ml_df.isnull().sum()
)


# ---------------------------------------------------------
# 10. Duplicate-date check
# ---------------------------------------------------------

print(
    "\nDuplicate dates:",
    ml_df["date"].duplicated().sum()
)

# ---------------------------------------------------------
# 11. Leakage sanity checks
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("LEAKAGE SANITY CHECK")
print("=" * 70)

# ---------------------------------------------------------
# Check lag_1
# ---------------------------------------------------------
#
# Compare from the SECOND row onward because the first
# row of ml_df has no previous row inside ml_df.
# ---------------------------------------------------------

lag_1_expected = ml_df["target"].shift(1)

lag_1_check = np.allclose(
    ml_df["lag_1"].iloc[1:].to_numpy(),
    lag_1_expected.iloc[1:].to_numpy()
)

print(
    "lag_1 uses previous target:",
    "PASS" if lag_1_check else "FAIL"
)


# ---------------------------------------------------------
# Check rolling_mean_3
# ---------------------------------------------------------

rolling_3_expected = (
    ml_df["target"]
    .shift(1)
    .rolling(3)
    .mean()
)

# The first three rows cannot be compared because the
# rolling calculation requires three previous observations.
rolling_3_check = np.allclose(
    ml_df["rolling_mean_3"].iloc[3:].to_numpy(),
    rolling_3_expected.iloc[3:].to_numpy()
)

print(
    "rolling_mean_3 uses historical data only:",
    "PASS" if rolling_3_check else "FAIL"
)


# ---------------------------------------------------------
# Check rolling_mean_6
# ---------------------------------------------------------

rolling_6_expected = (
    ml_df["target"]
    .shift(1)
    .rolling(6)
    .mean()
)

rolling_6_check = np.allclose(
    ml_df["rolling_mean_6"].iloc[6:].to_numpy(),
    rolling_6_expected.iloc[6:].to_numpy()
)

print(
    "rolling_mean_6 uses historical data only:",
    "PASS" if rolling_6_check else "FAIL"
)


# ---------------------------------------------------------
# Check rolling_mean_12
# ---------------------------------------------------------

rolling_12_expected = (
    ml_df["target"]
    .shift(1)
    .rolling(12)
    .mean()
)

rolling_12_check = np.allclose(
    ml_df["rolling_mean_12"].iloc[12:].to_numpy(),
    rolling_12_expected.iloc[12:].to_numpy()
)

print(
    "rolling_mean_12 uses historical data only:",
    "PASS" if rolling_12_check else "FAIL"
)


# ---------------------------------------------------------
# Final leakage result
# ---------------------------------------------------------

all_leakage_checks = (
    lag_1_check
    and rolling_3_check
    and rolling_6_check
    and rolling_12_check
)

print(
    "\nOverall feature leakage check:",
    "PASS" if all_leakage_checks else "FAIL"
)

if not all_leakage_checks:
    print(
        "\nWARNING: Feature construction requires investigation."
    )
else:
    print(
        "\nAll tested lag and rolling features use "
        "historical information only."
    )

# ---------------------------------------------------------
# 12. Save
# ---------------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

ml_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 70)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 70)

print(
    f"Saved to: {OUTPUT_FILE}"
)

print(
    f"Final shape: {ml_df.shape}"
)