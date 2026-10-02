import pandas as pd
from pathlib import Path

IIP_FILE = Path(
    "data/processed/iip_food_products_baseline_2012_2025.csv"
)

CPI_FILE = Path(
    "data/raw/external/cpi_general_all_india_2013_2025.csv"
)

OUTPUT_FILE = Path(
    "data/processed/iip_food_products_with_cpi_2013_2025.csv"
)

print("=" * 60)
print("IIP + CPI DATA ALIGNMENT")
print("=" * 60)

# ---------------------------------------------------------
# 1. Load datasets
# ---------------------------------------------------------

iip = pd.read_csv(IIP_FILE)
cpi = pd.read_csv(CPI_FILE)

# Convert dates
iip["date"] = pd.to_datetime(iip["date"])
cpi["date"] = pd.to_datetime(cpi["date"])

print("\nIIP:")
print(f"Rows: {len(iip)}")
print(f"Date range: {iip['date'].min()} → {iip['date'].max()}")

print("\nCPI:")
print(f"Rows: {len(cpi)}")
print(f"Date range: {cpi['date'].min()} → {cpi['date'].max()}")

# ---------------------------------------------------------
# 2. Check duplicate dates
# ---------------------------------------------------------

print("\nDuplicate IIP dates:", iip["date"].duplicated().sum())
print("Duplicate CPI dates:", cpi["date"].duplicated().sum())

# ---------------------------------------------------------
# 3. Merge using common dates
# ---------------------------------------------------------

merged = pd.merge(
    iip,
    cpi,
    on="date",
    how="inner"
)

merged = merged.sort_values("date").reset_index(drop=True)

# ---------------------------------------------------------
# 4. Validation
# ---------------------------------------------------------

print("\nMerged dataset:")
print(f"Rows: {len(merged)}")
print(f"Columns: {merged.columns.tolist()}")

print(
    f"Date range: "
    f"{merged['date'].min()} → {merged['date'].max()}"
)

print("\nMissing values:")
print(merged.isnull().sum())

print("\nFirst 5 rows:")
print(merged.head())

print("\nLast 5 rows:")
print(merged.tail())

# ---------------------------------------------------------
# 5. Expected checks
# ---------------------------------------------------------

expected_rows = 147
expected_start = pd.Timestamp("2013-01-01")
expected_end = pd.Timestamp("2025-03-01")

checks = {
    "Rows = 147": len(merged) == expected_rows,
    "Start = Jan 2013": merged["date"].min() == expected_start,
    "End = Mar 2025": merged["date"].max() == expected_end,
    "No duplicate dates": merged["date"].duplicated().sum() == 0,
    "No missing IIP index": merged["index"].isna().sum() == 0,
    "No missing CPI": merged["cpi_general_combined"].isna().sum() == 0,
}

print("\n" + "=" * 60)
print("ALIGNMENT VALIDATION")
print("=" * 60)

for check, result in checks.items():
    print(f"{check}: {'PASS' if result else 'FAIL'}")

# ---------------------------------------------------------
# 6. Save
# ---------------------------------------------------------

if all(checks.values()):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    merged.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nIIP + CPI alignment PASSED.")
    print(f"Saved to: {OUTPUT_FILE}")

else:
    print("\nIIP + CPI alignment FAILED.")
    print("Do not continue until the issue is investigated.")