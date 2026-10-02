from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "iip_multi_sector_2012_2025.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "graphs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

df = pd.read_csv(
    DATA_FILE,
    parse_dates=["date"]
)

df = df.sort_values(
    ["sector", "date"]
).reset_index(drop=True)


# ---------------------------------------------------------
# Basic validation
# ---------------------------------------------------------

sectors = sorted(df["sector"].unique())

print("=" * 70)
print("MULTI-SECTOR EDA")
print("=" * 70)

print(f"\nDataset shape: {df.shape}")
print(f"Number of sectors: {len(sectors)}")

print("\nSectors:")
for sector in sectors:
    print(f"- {sector}")


# ---------------------------------------------------------
# Basic statistics
# ---------------------------------------------------------

summary = (
    df.groupby("sector")["index"]
    .agg(
        observations="count",
        mean="mean",
        std="std",
        minimum="min",
        maximum="max"
    )
    .reset_index()
)

print("\n" + "=" * 70)
print("SECTOR SUMMARY STATISTICS")
print("=" * 70)

print(
    summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)


# ---------------------------------------------------------
# Annual averages
# ---------------------------------------------------------

annual = (
    df.groupby(["sector", "year"])["index"]
    .mean()
    .reset_index()
)

print("\n" + "=" * 70)
print("ANNUAL AVERAGES")
print("=" * 70)

for sector in sectors:

    print(f"\n{sector}")

    sector_annual = annual[
        annual["sector"] == sector
    ]

    print(
        sector_annual[
            ["year", "index"]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}"
        )
    )


# ---------------------------------------------------------
# Monthly seasonality
# ---------------------------------------------------------

monthly = (
    df.groupby(["sector", "month"])["index"]
    .mean()
    .reset_index()
)

print("\n" + "=" * 70)
print("MONTHLY SEASONALITY")
print("=" * 70)

for sector in sectors:

    sector_monthly = monthly[
        monthly["sector"] == sector
    ]

    highest = sector_monthly.loc[
        sector_monthly["index"].idxmax()
    ]

    lowest = sector_monthly.loc[
        sector_monthly["index"].idxmin()
    ]

    print(f"\n{sector}")
    print(
        f"Highest average month: "
        f"{highest['month']} "
        f"({highest['index']:.3f})"
    )

    print(
        f"Lowest average month: "
        f"{lowest['month']} "
        f"({lowest['index']:.3f})"
    )


# ---------------------------------------------------------
# Normalized sector comparison
# ---------------------------------------------------------
# Each sector is normalized to its first observation.
# This allows comparison of relative movement rather
# than raw index levels.

normalized = df.copy()

normalized["normalized_index"] = (
    normalized.groupby("sector")["index"]
    .transform(
        lambda x: (x / x.iloc[0]) * 100
    )
)


# ---------------------------------------------------------
# Plot 1 — Raw sector time series
# ---------------------------------------------------------

plt.figure(figsize=(14, 7))

for sector in sectors:

    sector_df = df[
        df["sector"] == sector
    ]

    plt.plot(
        sector_df["date"],
        sector_df["index"],
        label=sector
    )

plt.title(
    "Industrial Production Index — Sector Comparison"
)

plt.xlabel("Date")
plt.ylabel("IIP Index")

plt.legend()

plt.grid(True, alpha=0.3)

plt.tight_layout()

raw_plot = (
    OUTPUT_DIR
    / "multi_sector_iip_time_series.png"
)

plt.savefig(
    raw_plot,
    dpi=300
)

plt.close()


# ---------------------------------------------------------
# Plot 2 — Normalized comparison
# ---------------------------------------------------------

plt.figure(figsize=(14, 7))

for sector in sectors:

    sector_df = normalized[
        normalized["sector"] == sector
    ]

    plt.plot(
        sector_df["date"],
        sector_df["normalized_index"],
        label=sector
    )

plt.axhline(
    100,
    linestyle="--",
    linewidth=1
)

plt.title(
    "Normalized Sector Performance "
    "(First Observation = 100)"
)

plt.xlabel("Date")
plt.ylabel("Normalized Index")

plt.legend()

plt.grid(True, alpha=0.3)

plt.tight_layout()

normalized_plot = (
    OUTPUT_DIR
    / "multi_sector_normalized_comparison.png"
)

plt.savefig(
    normalized_plot,
    dpi=300
)

plt.close()


# ---------------------------------------------------------
# Plot 3 — Monthly seasonality
# ---------------------------------------------------------

plt.figure(figsize=(14, 7))

for sector in sectors:

    sector_monthly = monthly[
        monthly["sector"] == sector
    ]

    plt.plot(
        sector_monthly["month"],
        sector_monthly["index"],
        marker="o",
        label=sector
    )

plt.title(
    "Average Monthly Seasonality by Sector"
)

plt.xlabel("Month")
plt.ylabel("Average IIP Index")

plt.xticks(range(1, 13))

plt.legend()

plt.grid(True, alpha=0.3)

plt.tight_layout()

seasonality_plot = (
    OUTPUT_DIR
    / "multi_sector_monthly_seasonality.png"
)

plt.savefig(
    seasonality_plot,
    dpi=300
)

plt.close()


# ---------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------

pivot = df.pivot(
    index="date",
    columns="sector",
    values="index"
)

correlation = pivot.corr()

print("\n" + "=" * 70)
print("SECTOR CORRELATION MATRIX")
print("=" * 70)

print(
    correlation.to_string(
        float_format=lambda x: f"{x:.3f}"
    )
)


# ---------------------------------------------------------
# Save outputs
# ---------------------------------------------------------

summary_file = (
    PROJECT_ROOT
    / "outputs"
    / "multi_sector_summary.csv"
)

correlation_file = (
    PROJECT_ROOT
    / "outputs"
    / "multi_sector_correlation.csv"
)

summary.to_csv(
    summary_file,
    index=False
)

correlation.to_csv(
    correlation_file
)


# ---------------------------------------------------------
# Final message
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("MULTI-SECTOR EDA COMPLETED")
print("=" * 70)

print("\nGraphs saved:")

print(raw_plot)
print(normalized_plot)
print(seasonality_plot)

print("\nData outputs saved:")

print(summary_file)
print(correlation_file)

print("\n" + "=" * 70)