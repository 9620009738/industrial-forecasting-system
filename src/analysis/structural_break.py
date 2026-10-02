import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = "data/processed/iip_multi_sector_2012_2025.csv"

OUTPUT_DIR = "outputs/structural_breaks"
GRAPH_DIR = "outputs/graphs/structural_breaks"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)


# =========================================================
# Pettitt's Change-Point Test
# =========================================================

def pettitt_test(series):
    """
    Pettitt's non-parametric change-point test.

    Returns:
        change_index
        change_statistic
        p_value
    """

    values = np.asarray(series, dtype=float)

    n = len(values)

    # Rank the observations
    ranks = pd.Series(values).rank(
        method="average"
    ).to_numpy()

    # Pettitt U statistic for each possible split point
    cumulative_rank_sum = np.cumsum(ranks)

    t = np.arange(1, n + 1)

    U = (
        2 * cumulative_rank_sum
        - t * (n + 1)
    )

    # The final observation is not a valid split
    U[-1] = 0

    # Locate maximum absolute statistic
    change_index = int(
        np.argmax(np.abs(U))
    )

    K = float(
        np.abs(U[change_index])
    )

    # Approximate two-sided Pettitt p-value
    p_value = (
        2
        * np.exp(
            (-6 * K**2)
            / (n**3 + n**2)
        )
    )

    p_value = min(
        float(p_value),
        1.0
    )

    return (
        change_index,
        K,
        p_value
    )


# =========================================================
# Load data
# =========================================================

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    ["sector", "date"]
).reset_index(drop=True)


# =========================================================
# Storage
# =========================================================

break_results = []


# =========================================================
# Analyze each sector
# =========================================================

for sector in df["sector"].unique():

    print("\n" + "=" * 70)
    print(f"STRUCTURAL BREAK ANALYSIS: {sector}")
    print("=" * 70)

    sector_df = (
        df[df["sector"] == sector]
        .copy()
        .sort_values("date")
        .reset_index(drop=True)
    )

    series = sector_df["index"].astype(float)

    # -----------------------------------------------------
    # Pettitt test
    # -----------------------------------------------------

    change_index, statistic, p_value = pettitt_test(
        series
    )

    change_date = sector_df.loc[
        change_index,
        "date"
    ]

    change_value = sector_df.loc[
        change_index,
        "index"
    ]

    # -----------------------------------------------------
    # Significance decision
    # -----------------------------------------------------

    significant = p_value < 0.05

    # -----------------------------------------------------
    # Before/after statistics
    # -----------------------------------------------------

    before = series.iloc[
        :change_index
    ]

    after = series.iloc[
        change_index:
    ]

    before_mean = (
        before.mean()
        if len(before) > 0
        else np.nan
    )

    after_mean = (
        after.mean()
        if len(after) > 0
        else np.nan
    )

    before_std = (
        before.std()
        if len(before) > 1
        else np.nan
    )

    after_std = (
        after.std()
        if len(after) > 1
        else np.nan
    )

    mean_change = (
        after_mean - before_mean
    )

    # -----------------------------------------------------
    # Store result
    # -----------------------------------------------------

    break_results.append(
        {
            "sector": sector,
            "observations": len(series),
            "break_date": change_date,
            "break_index_value": change_value,
            "pettitt_statistic": statistic,
            "p_value": p_value,
            "significant_at_5_percent": significant,
            "before_mean": before_mean,
            "after_mean": after_mean,
            "before_std": before_std,
            "after_std": after_std,
            "mean_change": mean_change
        }
    )

    # -----------------------------------------------------
    # Print result
    # -----------------------------------------------------

    print(
        f"Candidate break date: "
        f"{change_date.strftime('%Y-%m-%d')}"
    )

    print(
        f"Index at candidate break: "
        f"{change_value:.2f}"
    )

    print(
        f"Pettitt statistic: "
        f"{statistic:.2f}"
    )

    print(
        f"P-value: "
        f"{p_value:.6f}"
    )

    print(
        f"Significant at 5%: "
        f"{significant}"
    )

    print(
        f"Mean before break: "
        f"{before_mean:.2f}"
    )

    print(
        f"Mean after break: "
        f"{after_mean:.2f}"
    )

    print(
        f"Mean change: "
        f"{mean_change:.2f}"
    )

    # -----------------------------------------------------
    # Visualization
    # -----------------------------------------------------

    plt.figure(figsize=(14, 6))

    plt.plot(
        sector_df["date"],
        sector_df["index"],
        label="Observed IIP Index"
    )

    plt.axvline(
        change_date,
        linestyle="--",
        label="Candidate Structural Break"
    )

    plt.scatter(
        [change_date],
        [change_value],
        s=80,
        label="Detected Point"
    )

    plt.title(
        f"Structural Break Detection - {sector}"
    )

    plt.xlabel("Date")
    plt.ylabel("IIP Index")

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    safe_name = (
        sector
        .lower()
        .replace(" ", "_")
        .replace(",", "")
        .replace("-", "_")
    )

    graph_path = os.path.join(
        GRAPH_DIR,
        f"{safe_name}_structural_break.png"
    )

    plt.savefig(
        graph_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Graph saved: {graph_path}"
    )


# =========================================================
# Create result dataframe
# =========================================================

break_df = pd.DataFrame(
    break_results
)


# =========================================================
# Save results
# =========================================================

results_path = os.path.join(
    OUTPUT_DIR,
    "multi_sector_structural_breaks.csv"
)

break_df.to_csv(
    results_path,
    index=False
)


# =========================================================
# Final output
# =========================================================

print("\n" + "=" * 70)
print("STRUCTURAL BREAK ANALYSIS COMPLETED")
print("=" * 70)

print("\nResults:")

print(
    break_df.to_string(index=False)
)

print(
    f"\nResults saved to:\n{results_path}"
)

print(
    f"\nGraphs saved to:\n{GRAPH_DIR}"
)