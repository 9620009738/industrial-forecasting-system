import pandas as pd
from pathlib import Path

FILE = Path("data/raw/external/cpi_general_all_india_2013_2025.csv")

print("=" * 60)
print("CPI DATA VALIDATION")
print("=" * 60)

df = pd.read_csv(FILE)

print("\nColumns:")
print(df.columns.tolist())

print("\nShape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nLast 5 rows:")
print(df.tail())

# Convert date
df["date"] = pd.to_datetime(df["date"])

# Sort
df = df.sort_values("date").reset_index(drop=True)

print("\nDate range:")
print(df["date"].min())
print(df["date"].max())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate dates:")
print(df["date"].duplicated().sum())

# Expected monthly frequency
expected_dates = pd.date_range(
    start=df["date"].min(),
    end=df["date"].max(),
    freq="MS"
)

print("\nExpected number of months:")
print(len(expected_dates))

print("\nActual number of rows:")
print(len(df))

# Check missing months
missing_dates = expected_dates.difference(df["date"])

print("\nMissing months:")
print(missing_dates.tolist())

# Check duplicate dates
duplicate_dates = df[df["date"].duplicated(keep=False)]

if len(duplicate_dates) > 0:
    print("\nDuplicate date records:")
    print(duplicate_dates)

# CPI statistics
print("\nCPI statistics:")
print(df["cpi_general_combined"].describe())

# Required checks
checks = {
    "Rows = 147": len(df) == 147,
    "Start = 2013-01-01": df["date"].min() == pd.Timestamp("2013-01-01"),
    "End = 2025-03-01": df["date"].max() == pd.Timestamp("2025-03-01"),
    "No missing CPI": df["cpi_general_combined"].isna().sum() == 0,
    "No duplicate dates": df["date"].duplicated().sum() == 0,
    "No missing months": len(missing_dates) == 0,
}

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

for check, result in checks.items():
    print(f"{check}: {'PASS' if result else 'FAIL'}")

if all(checks.values()):
    print("\nCPI DATA VALIDATION PASSED.")
else:
    print("\nCPI DATA VALIDATION FAILED.")