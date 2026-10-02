import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.tsa.seasonal import STL
from sklearn.ensemble import IsolationForest


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

INPUT_FILE = "data/processed/iip_multi_sector_2012_2025.csv"

OUTPUT_DIR = "outputs/anomalies"
GRAPH_DIR = "outputs/graphs/anomalies"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    ["sector", "date"]
).reset_index(drop=True)


# ---------------------------------------------------------
# Storage
# ---------------------------------------------------------

all_results = []
summary_results = []


# ---------------------------------------------------------
# Process each sector independently
# ---------------------------------------------------------

for sector in df["sector"].unique():

    print("\n" + "=" * 70)
    print(f"ANALYZING SECTOR: {sector}")
    print("=" * 70)

    sector_df = (
        df[df["sector"] == sector]
        .copy()
        .sort_values("date")
        .reset_index(drop=True)
    )

    sector_df = sector_df.set_index("date")

    series = sector_df["index"].astype(float)

    # -----------------------------------------------------
    # STL decomposition
    # -----------------------------------------------------
    # STL separates:
    # Observed = Trend + Seasonal + Residual
    #
    # This is important because normal seasonal movements
    # should not automatically be classified as anomalies.
    # -----------------------------------------------------

    stl = STL(
        series,
        period=12,
        robust=True
    )

    decomposition = stl.fit()

    sector_df["trend"] = decomposition.trend
    sector_df["seasonal"] = decomposition.seasonal
    sector_df["residual"] = decomposition.resid

    # -----------------------------------------------------
    # Robust statistical anomaly detection
    # -----------------------------------------------------

    residual = sector_df["residual"]

    residual_median = residual.median()

    mad = np.median(
        np.abs(residual - residual_median)
    )

    # Convert MAD to a robust standard deviation estimate
    robust_scale = 1.4826 * mad

    # Fallback if MAD is zero
    if robust_scale == 0:

        robust_scale = residual.std()

    # Final fallback
    if robust_scale == 0 or np.isnan(robust_scale):

        robust_scale = 1.0

    sector_df["robust_z_score"] = (
        residual - residual_median
    ) / robust_scale

    # Common robust anomaly threshold
    sector_df["statistical_anomaly"] = (
        sector_df["robust_z_score"].abs() >= 3.5
    )

    # -----------------------------------------------------
    # Isolation Forest
    # -----------------------------------------------------
    # Features include:
    #   index
    #   residual
    #   month
    #
    # Month is represented cyclically so that December and
    # January remain close to each other.
    # -----------------------------------------------------

    sector_df["month"] = sector_df.index.month

    sector_df["month_sin"] = np.sin(
        2 * np.pi * sector_df["month"] / 12
    )

    sector_df["month_cos"] = np.cos(
        2 * np.pi * sector_df["month"] / 12
    )

    features = sector_df[
        [
            "index",
            "residual",
            "month_sin",
            "month_cos"
        ]
    ].copy()

    isolation_forest = IsolationForest(
        n_estimators=300,
        contamination=0.05,
        random_state=42
    )

    isolation_forest.fit(features)

    sector_df["iforest_prediction"] = (
        isolation_forest.predict(features)
    )

    sector_df["iforest_score"] = (
        isolation_forest.decision_function(features)
    )

    sector_df["isolation_forest_anomaly"] = (
        sector_df["iforest_prediction"] == -1
    )

    # -----------------------------------------------------
    # Combined anomaly indicator
    # -----------------------------------------------------

    sector_df["anomaly_method_count"] = (
        sector_df["statistical_anomaly"].astype(int)
        +
        sector_df["isolation_forest_anomaly"].astype(int)
    )

    sector_df["anomaly_flag"] = (
        sector_df["anomaly_method_count"] > 0
    )

    # -----------------------------------------------------
    # Add sector column back
    # -----------------------------------------------------

    sector_df["sector"] = sector

    sector_df = sector_df.reset_index()

    # -----------------------------------------------------
    # Store results
    # -----------------------------------------------------

    all_results.append(
        sector_df[
            [
                "date",
                "sector",
                "index",
                "trend",
                "seasonal",
                "residual",
                "robust_z_score",
                "statistical_anomaly",
                "iforest_score",
                "isolation_forest_anomaly",
                "anomaly_method_count",
                "anomaly_flag"
            ]
        ]
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    statistical_count = int(
        sector_df["statistical_anomaly"].sum()
    )

    isolation_count = int(
        sector_df["isolation_forest_anomaly"].sum()
    )

    combined_count = int(
        sector_df["anomaly_flag"].sum()
    )

    summary_results.append(
        {
            "sector": sector,
            "observations": len(sector_df),
            "statistical_anomalies": statistical_count,
            "isolation_forest_anomalies": isolation_count,
            "combined_anomalies": combined_count
        }
    )

    # -----------------------------------------------------
    # Print anomaly dates
    # -----------------------------------------------------

    detected = sector_df[
        sector_df["anomaly_flag"]
    ].copy()

    print(f"Observations: {len(sector_df)}")
    print(
        f"Statistical anomalies: {statistical_count}"
    )
    print(
        f"Isolation Forest anomalies: {isolation_count}"
    )
    print(
        f"Combined anomaly observations: {combined_count}"
    )

    if len(detected) > 0:

        print("\nDetected observations:")

        print(
            detected[
                [
                    "date",
                    "index",
                    "residual",
                    "robust_z_score",
                    "statistical_anomaly",
                    "isolation_forest_anomaly"
                ]
            ].to_string(index=False)
        )

    else:

        print("\nNo anomalies detected.")


    # -----------------------------------------------------
    # Visualization
    # -----------------------------------------------------

    plt.figure(figsize=(14, 6))

    plt.plot(
        sector_df["date"],
        sector_df["index"],
        label="Observed Index"
    )

    # Statistical anomalies
    statistical_points = sector_df[
        sector_df["statistical_anomaly"]
    ]

    if len(statistical_points) > 0:

        plt.scatter(
            statistical_points["date"],
            statistical_points["index"],
            marker="o",
            s=70,
            label="Statistical Anomaly"
        )

    # Isolation Forest anomalies
    isolation_points = sector_df[
        sector_df["isolation_forest_anomaly"]
    ]

    if len(isolation_points) > 0:

        plt.scatter(
            isolation_points["date"],
            isolation_points["index"],
            marker="x",
            s=80,
            label="Isolation Forest Anomaly"
        )

    plt.title(
        f"Anomaly Detection - {sector}"
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
        f"{safe_name}_anomalies.png"
    )

    plt.savefig(
        graph_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nGraph saved: {graph_path}"
    )


# ---------------------------------------------------------
# Combine all sectors
# ---------------------------------------------------------

anomaly_results = pd.concat(
    all_results,
    ignore_index=True
)

summary_df = pd.DataFrame(
    summary_results
)


# ---------------------------------------------------------
# Save detailed results
# ---------------------------------------------------------

results_path = os.path.join(
    OUTPUT_DIR,
    "multi_sector_anomalies.csv"
)

anomaly_results.to_csv(
    results_path,
    index=False
)


# ---------------------------------------------------------
# Save summary
# ---------------------------------------------------------

summary_path = os.path.join(
    OUTPUT_DIR,
    "anomaly_summary.csv"
)

summary_df.to_csv(
    summary_path,
    index=False
)


# ---------------------------------------------------------
# Final report
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("ANOMALY DETECTION COMPLETED")
print("=" * 70)

print("\nSummary:")
print(summary_df.to_string(index=False))

print(
    f"\nDetailed results saved to:\n{results_path}"
)

print(
    f"\nSummary saved to:\n{summary_path}"
)

print(
    f"\nGraphs saved to:\n{GRAPH_DIR}"
)