import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.stattools import adfuller


INPUT_FILE = Path(
    "data/processed/iip_food_products_with_cpi_2013_2025.csv"
)

OUTPUT_DIR = Path("outputs/analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("IIP + CPI EXTERNAL VARIABLE ANALYSIS")
print("=" * 70)


# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)

print("\nDataset:")
print(f"Rows: {len(df)}")
print(f"Date range: {df['date'].min()} → {df['date'].max()}")


# ---------------------------------------------------------
# 2. Basic statistics
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("BASIC STATISTICS")
print("=" * 70)

print(
    df[
        ["index", "cpi_general_combined"]
    ].describe()
)


# ---------------------------------------------------------
# 3. Correlation
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("CORRELATION")
print("=" * 70)

correlation = df[
    ["index", "cpi_general_combined"]
].corr()

print(correlation)

print(
    f"\nIIP-CPI Pearson correlation: "
    f"{correlation.loc['index', 'cpi_general_combined']:.4f}"
)


# ---------------------------------------------------------
# 4. CPI month-to-month change
# ---------------------------------------------------------

df["cpi_change"] = df["cpi_general_combined"].diff()

df["iip_change"] = df["index"].diff()


print("\n" + "=" * 70)
print("CHANGE-SERIES CORRELATION")
print("=" * 70)

change_corr = df[
    ["iip_change", "cpi_change"]
].corr()

print(change_corr)

print(
    f"\nCorrelation between monthly IIP change "
    f"and monthly CPI change: "
    f"{change_corr.loc['iip_change', 'cpi_change']:.4f}"
)


# ---------------------------------------------------------
# 5. Lagged correlations
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("LAGGED CPI CORRELATION")
print("=" * 70)

lag_results = []

for lag in range(0, 7):

    temp = pd.DataFrame({
        "iip": df["index"],
        "cpi": df["cpi_general_combined"].shift(lag)
    }).dropna()

    corr = temp["iip"].corr(temp["cpi"])

    lag_results.append({
        "lag_months": lag,
        "correlation": corr
    })

    print(
        f"CPI lag {lag} month(s): "
        f"{corr:.4f}"
    )

lag_df = pd.DataFrame(lag_results)

lag_df.to_csv(
    OUTPUT_DIR / "iip_cpi_lagged_correlations.csv",
    index=False
)


# ---------------------------------------------------------
# 6. ADF test for CPI
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("ADF TEST — CPI LEVEL")
print("=" * 70)

cpi = df["cpi_general_combined"].dropna()

adf_result = adfuller(cpi, autolag="AIC")

print(f"ADF Statistic: {adf_result[0]:.6f}")
print(f"p-value:       {adf_result[1]:.6f}")
print(f"Lags used:     {adf_result[2]}")
print(f"Observations:  {adf_result[3]}")

for key, value in adf_result[4].items():
    print(f"Critical {key}: {value:.6f}")

if adf_result[1] < 0.05:
    print("\nConclusion: CPI level is stationary at 5%.")
else:
    print("\nConclusion: CPI level is non-stationary at 5%.")


# ---------------------------------------------------------
# 7. ADF test — CPI first difference
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("ADF TEST — CPI FIRST DIFFERENCE")
print("=" * 70)

cpi_diff = cpi.diff().dropna()

adf_diff = adfuller(cpi_diff, autolag="AIC")

print(f"ADF Statistic: {adf_diff[0]:.6f}")
print(f"p-value:       {adf_diff[1]:.6f}")
print(f"Lags used:     {adf_diff[2]}")
print(f"Observations:  {adf_diff[3]}")

for key, value in adf_diff[4].items():
    print(f"Critical {key}: {value:.6f}")

if adf_diff[1] < 0.05:
    print(
        "\nConclusion: First-differenced CPI "
        "is stationary at 5%."
    )
else:
    print(
        "\nConclusion: First-differenced CPI "
        "is non-stationary at 5%."
    )


# ---------------------------------------------------------
# 8. Forecast train/test split
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("FORECAST SPLIT / LEAKAGE CHECK")
print("=" * 70)

train_end = pd.Timestamp("2024-03-01")
test_start = pd.Timestamp("2024-04-01")
test_end = pd.Timestamp("2025-03-01")

train = df[df["date"] <= train_end].copy()

test = df[
    (df["date"] >= test_start) &
    (df["date"] <= test_end)
].copy()

print(f"Training period: {train['date'].min()} → {train['date'].max()}")
print(f"Training rows:   {len(train)}")

print(f"\nTest period:     {test['date'].min()} → {test['date'].max()}")
print(f"Test rows:       {len(test)}")


# ---------------------------------------------------------
# 9. Leakage checks
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("LEAKAGE CHECK")
print("=" * 70)

checks = {
    "Training ends before test": train["date"].max() < test["date"].min(),
    "Training contains no test dates":
        not train["date"].isin(test["date"]).any(),
    "Test contains 12 months": len(test) == 12,
    "No missing CPI in training":
        train["cpi_general_combined"].isna().sum() == 0,
    "No missing CPI in test":
        test["cpi_general_combined"].isna().sum() == 0,
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")


# ---------------------------------------------------------
# 10. Save summary
# ---------------------------------------------------------

summary = pd.DataFrame({
    "metric": [
        "observations",
        "iip_cpi_correlation",
        "iip_cpi_change_correlation",
        "cpi_adf_pvalue",
        "cpi_difference_adf_pvalue",
        "training_observations",
        "test_observations"
    ],
    "value": [
        len(df),
        correlation.loc["index", "cpi_general_combined"],
        change_corr.loc["iip_change", "cpi_change"],
        adf_result[1],
        adf_diff[1],
        len(train),
        len(test)
    ]
})

summary.to_csv(
    OUTPUT_DIR / "iip_cpi_analysis_summary.csv",
    index=False
)


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print(
    "\nSaved:"
    "\noutputs/analysis/iip_cpi_lagged_correlations.csv"
    "\noutputs/analysis/iip_cpi_analysis_summary.csv"
)