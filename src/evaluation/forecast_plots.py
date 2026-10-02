import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = (
    "data/processed/"
    "iip_food_products_baseline_2012_2025.csv"
)

FORECAST_DIR = "outputs/forecasts"
GRAPH_DIR = "outputs/graphs"

START_DATE = "2024-04-01"
END_DATE = "2025-03-01"

os.makedirs(GRAPH_DIR, exist_ok=True)


# ============================================================
# LOAD ACTUAL DATA
# ============================================================

actual_df = pd.read_csv(DATA_PATH)

actual_df["date"] = pd.to_datetime(
    actual_df["date"]
)

actual_df = actual_df[
    (actual_df["date"] >= START_DATE)
    &
    (actual_df["date"] <= END_DATE)
].copy()

actual_df = actual_df[
    ["date", "index"]
].rename(
    columns={"index": "actual"}
)


# ============================================================
# FORECAST FILE DEFINITIONS
# ============================================================

forecast_files = {
    "TESM": "tesm_baseline_forecast.csv",
    "Paper SARIMA": "sarima_baseline_forecast.csv",
    "Random Forest": "random_forest_final_forecast.csv",
    "XGBoost": "xgboost_final_forecast.csv",
    "LSTM": "lstm_final_test.csv",
    "GRU": "gru_final_test.csv"
}


# ============================================================
# LOAD AND VALIDATE FORECASTS
# ============================================================

forecast_data = {}

for model_name, filename in forecast_files.items():

    path = os.path.join(
        FORECAST_DIR,
        filename
    )

    forecast_df = pd.read_csv(path)

    forecast_df["date"] = pd.to_datetime(
        forecast_df["date"]
    )

    forecast_df = forecast_df[
        (forecast_df["date"] >= START_DATE)
        &
        (forecast_df["date"] <= END_DATE)
    ].copy()

    if len(forecast_df) != 12:

        raise ValueError(
            f"{model_name} forecast contains "
            f"{len(forecast_df)} rows instead of 12."
        )

    # Detect forecast column
    if "forecast" in forecast_df.columns:

        forecast_column = "forecast"

    elif "predicted" in forecast_df.columns:

        forecast_column = "predicted"

    else:

        raise ValueError(
            f"Could not find forecast column "
            f"in {filename}."
        )

    forecast_data[model_name] = forecast_df[
        ["date", forecast_column]
    ].rename(
        columns={
            forecast_column: model_name
        }
    )


# ============================================================
# MERGE ALL FORECASTS
# ============================================================

comparison_df = actual_df.copy()

for model_name, forecast_df in forecast_data.items():

    comparison_df = comparison_df.merge(
        forecast_df,
        on="date",
        how="left"
    )


# ============================================================
# VALIDATION
# ============================================================

if len(comparison_df) != 12:

    raise ValueError(
        "Final comparison does not contain exactly "
        "12 monthly observations."
    )

if comparison_df.isna().any().any():

    raise ValueError(
        "Missing values detected in actual/forecast "
        "comparison."
    )


# ============================================================
# SAVE COMBINED DATA
# ============================================================

comparison_df.to_csv(
    f"{FORECAST_DIR}/all_models_final_forecast_comparison.csv",
    index=False
)


# ============================================================
# 1. ALL MODELS — ACTUAL VS FORECAST
# ============================================================

plt.figure(figsize=(15, 8))

plt.plot(
    comparison_df["date"],
    comparison_df["actual"],
    marker="o",
    linewidth=3,
    label="Actual"
)

for model_name in forecast_files:

    plt.plot(
        comparison_df["date"],
        comparison_df[model_name],
        marker="o",
        linewidth=1.5,
        label=model_name
    )

plt.title(
    "Actual vs Forecast — Final Test Period"
)

plt.xlabel("Month")
plt.ylabel("IIP Index")

plt.xticks(
    comparison_df["date"],
    comparison_df["date"].dt.strftime("%b %Y"),
    rotation=45
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/actual_vs_all_models_final_test.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 2. STATISTICAL MODELS
# ============================================================

statistical_models = [
    "TESM",
    "Paper SARIMA"
]

plt.figure(figsize=(15, 8))

plt.plot(
    comparison_df["date"],
    comparison_df["actual"],
    marker="o",
    linewidth=3,
    label="Actual"
)

for model_name in statistical_models:

    plt.plot(
        comparison_df["date"],
        comparison_df[model_name],
        marker="o",
        linewidth=2,
        label=model_name
    )

plt.title(
    "Statistical Models — Actual vs Forecast"
)

plt.xlabel("Month")
plt.ylabel("IIP Index")

plt.xticks(
    comparison_df["date"],
    comparison_df["date"].dt.strftime("%b %Y"),
    rotation=45
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/actual_vs_statistical_models.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 3. MACHINE LEARNING / DEEP LEARNING
# ============================================================

ml_models = [
    "Random Forest",
    "XGBoost",
    "LSTM",
    "GRU"
]

plt.figure(figsize=(15, 8))

plt.plot(
    comparison_df["date"],
    comparison_df["actual"],
    marker="o",
    linewidth=3,
    label="Actual"
)

for model_name in ml_models:

    plt.plot(
        comparison_df["date"],
        comparison_df[model_name],
        marker="o",
        linewidth=1.8,
        label=model_name
    )

plt.title(
    "Machine Learning and Deep Learning Models — "
    "Actual vs Forecast"
)

plt.xlabel("Month")
plt.ylabel("IIP Index")

plt.xticks(
    comparison_df["date"],
    comparison_df["date"].dt.strftime("%b %Y"),
    rotation=45
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/actual_vs_ml_models.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 4. FORECAST ERROR DATA
# ============================================================

for model_name in forecast_files:

    comparison_df[
        f"{model_name}_error"
    ] = (
        comparison_df[model_name]
        - comparison_df["actual"]
    )


comparison_df.to_csv(
    f"{FORECAST_DIR}/all_models_final_forecast_errors.csv",
    index=False
)


# ============================================================
# 5. FORECAST ERROR PLOT
# ============================================================

plt.figure(figsize=(15, 8))

for model_name in forecast_files:

    plt.plot(
        comparison_df["date"],
        comparison_df[
            f"{model_name}_error"
        ],
        marker="o",
        linewidth=1.5,
        label=model_name
    )

plt.axhline(
    0,
    linewidth=1
)

plt.title(
    "Forecast Error — Final Test Period"
)

plt.xlabel("Month")
plt.ylabel("Forecast Error (Forecast − Actual)")

plt.xticks(
    comparison_df["date"],
    comparison_df["date"].dt.strftime("%b %Y"),
    rotation=45
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/forecast_errors_all_models.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print("=" * 70)
print("ACTUAL VS FORECAST ANALYSIS COMPLETE")
print("=" * 70)

print("\nFinal test period:")
print(
    comparison_df["date"].min().strftime("%Y-%m"),
    "to",
    comparison_df["date"].max().strftime("%Y-%m")
)

print(
    "Observations:",
    len(comparison_df)
)

print("\nSaved data:")
print(
    "outputs/forecasts/"
    "all_models_final_forecast_comparison.csv"
)

print(
    "outputs/forecasts/"
    "all_models_final_forecast_errors.csv"
)

print("\nSaved graphs:")
print(
    "outputs/graphs/"
    "actual_vs_all_models_final_test.png"
)

print(
    "outputs/graphs/"
    "actual_vs_statistical_models.png"
)

print(
    "outputs/graphs/"
    "actual_vs_ml_models.png"
)

print(
    "outputs/graphs/"
    "forecast_errors_all_models.png"
)