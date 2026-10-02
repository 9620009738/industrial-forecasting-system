import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/iip_food_products_ml_features.csv"
)


print("=" * 70)
print("ML TIME-SERIES TRAIN / VALIDATION / TEST DESIGN")
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


print("\nDataset:")
print(f"Rows: {len(df)}")
print(
    f"Date range: "
    f"{df['date'].min()} → {df['date'].max()}"
)


# ---------------------------------------------------------
# 2. Final untouched test set
# ---------------------------------------------------------

final_test_start = pd.Timestamp("2024-04-01")

development = df[
    df["date"] < final_test_start
].copy()

final_test = df[
    df["date"] >= final_test_start
].copy()


print("\n" + "=" * 70)
print("FINAL TEST SPLIT")
print("=" * 70)

print(
    f"Development: "
    f"{development['date'].min()} → "
    f"{development['date'].max()}"
)

print(
    f"Development rows: {len(development)}"
)

print(
    f"\nFinal test: "
    f"{final_test['date'].min()} → "
    f"{final_test['date'].max()}"
)

print(
    f"Final test rows: {len(final_test)}"
)


# ---------------------------------------------------------
# 3. Walk-forward origins
# ---------------------------------------------------------
#
# Use the same historical forecast periods as our
# matched SARIMA/SARIMAX experiment:
#
# 2021
# 2022
# 2023
#
# Each forecast horizon = 12 months.
# ---------------------------------------------------------

forecast_periods = [
    (
        "2021",
        pd.Timestamp("2021-01-01"),
        pd.Timestamp("2021-12-01")
    ),
    (
        "2022",
        pd.Timestamp("2022-01-01"),
        pd.Timestamp("2022-12-01")
    ),
    (
        "2023",
        pd.Timestamp("2023-01-01"),
        pd.Timestamp("2023-12-01")
    ),
]


print("\n" + "=" * 70)
print("WALK-FORWARD VALIDATION PERIODS")
print("=" * 70)


validation_results = []


for name, forecast_start, forecast_end in forecast_periods:

    train = development[
        development["date"] < forecast_start
    ].copy()

    validation = development[
        (development["date"] >= forecast_start)
        &
        (development["date"] <= forecast_end)
    ].copy()

    validation_results.append({
        "period": name,
        "train_start": train["date"].min(),
        "train_end": train["date"].max(),
        "train_rows": len(train),
        "validation_start": validation["date"].min(),
        "validation_end": validation["date"].max(),
        "validation_rows": len(validation)
    })


validation_df = pd.DataFrame(
    validation_results
)


print(
    validation_df.to_string(index=False)
)


# ---------------------------------------------------------
# 4. Leakage checks
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("TIME-SERIES LEAKAGE CHECK")
print("=" * 70)


checks = {}


# Final test must contain exactly 12 observations
checks["Final test has 12 observations"] = (
    len(final_test) == 12
)


# Final test must start in April 2024
checks["Final test starts Apr 2024"] = (
    final_test["date"].min()
    == pd.Timestamp("2024-04-01")
)


# Final test must end in March 2025
checks["Final test ends Mar 2025"] = (
    final_test["date"].max()
    == pd.Timestamp("2025-03-01")
)


# Development and final test must not overlap
checks["Development/test overlap = 0"] = (
    len(
        set(development["date"])
        &
        set(final_test["date"])
    )
    == 0
)


# Every validation period must have 12 observations
checks["Every validation period has 12 rows"] = (
    validation_df["validation_rows"].eq(12).all()
)


# Training must end before validation begins
checks["Training precedes validation"] = all(
    row["train_end"] < row["validation_start"]
    for _, row in validation_df.iterrows()
)


for name, result in checks.items():

    print(
        f"{name}: "
        f"{'PASS' if result else 'FAIL'}"
    )


all_pass = all(checks.values())


print("\n" + "=" * 70)

if all_pass:
    print("ML SPLIT VALIDATION PASSED.")
else:
    print("ML SPLIT VALIDATION FAILED.")

print("=" * 70)