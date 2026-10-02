from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "iip_food_products_baseline_2012_2025.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "final_baseline_evaluation.csv"


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

def calculate_mape(actual, predicted):
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    mask = actual != 0

    return np.mean(
        np.abs(
            (actual[mask] - predicted[mask])
            / actual[mask]
        )
    ) * 100


def calculate_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    mape = calculate_mape(actual, predicted)

    return mae, rmse, mape


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("=" * 70)
print("FINAL BASELINE MODEL EVALUATION")
print("=" * 70)

df = pd.read_csv(DATA_FILE, parse_dates=["date"])

df = df.sort_values("date").reset_index(drop=True)

print(f"\nDataset rows: {len(df)}")
print(f"First date: {df['date'].min().date()}")
print(f"Last date:  {df['date'].max().date()}")


# ---------------------------------------------------------
# Final untouched train/test split
# ---------------------------------------------------------

TEST_SIZE = 12

train = df.iloc[:-TEST_SIZE].copy()
test = df.iloc[-TEST_SIZE:].copy()

y_train = train["index"].astype(float)
y_test = test["index"].astype(float)

print("\nFinal evaluation split:")
print(
    f"Training: {train['date'].min().date()} "
    f"to {train['date'].max().date()} "
    f"({len(train)} observations)"
)

print(
    f"Testing:  {test['date'].min().date()} "
    f"to {test['date'].max().date()} "
    f"({len(test)} observations)"
)

print("\nTest observations:")
print(
    test[["date", "index"]]
    .to_string(index=False)
)


# ---------------------------------------------------------
# Storage
# ---------------------------------------------------------

results = []


# =========================================================
# MODEL 1 — TESM / Holt-Winters
# =========================================================

print("\n" + "=" * 70)
print("1. TESM / HOLT-WINTERS")
print("=" * 70)

tesm_model = ExponentialSmoothing(
    y_train,
    trend="add",
    seasonal="add",
    seasonal_periods=12,
    initialization_method="estimated"
)

tesm_fit = tesm_model.fit(
    optimized=True
)

tesm_forecast = tesm_fit.forecast(TEST_SIZE)

tesm_mae, tesm_rmse, tesm_mape = calculate_metrics(
    y_test,
    tesm_forecast
)

print(f"MAE:  {tesm_mae:.6f}")
print(f"RMSE: {tesm_rmse:.6f}")
print(f"MAPE: {tesm_mape:.6f}%")


results.append({
    "model": "TESM",
    "order": "",
    "seasonal_order": "",
    "MAE": tesm_mae,
    "RMSE": tesm_rmse,
    "MAPE": tesm_mape
})


# =========================================================
# MODEL 2 — PAPER SARIMA
# SARIMA(1,1,1)(1,1,1,12)
# =========================================================

print("\n" + "=" * 70)
print("2. PAPER SARIMA")
print("=" * 70)

paper_order = (1, 1, 1)
paper_seasonal_order = (1, 1, 1, 12)

paper_model = SARIMAX(
    y_train,
    order=paper_order,
    seasonal_order=paper_seasonal_order,
    enforce_stationarity=False,
    enforce_invertibility=False
)

paper_fit = paper_model.fit(
    disp=False
)

paper_forecast = paper_fit.forecast(TEST_SIZE)

paper_mae, paper_rmse, paper_mape = calculate_metrics(
    y_test,
    paper_forecast
)

print(f"Order: {paper_order}")
print(f"Seasonal order: {paper_seasonal_order}")
print(f"MAE:  {paper_mae:.6f}")
print(f"RMSE: {paper_rmse:.6f}")
print(f"MAPE: {paper_mape:.6f}%")
print(f"AIC:  {paper_fit.aic:.6f}")


results.append({
    "model": "Paper SARIMA",
    "order": str(paper_order),
    "seasonal_order": str(paper_seasonal_order),
    "MAE": paper_mae,
    "RMSE": paper_rmse,
    "MAPE": paper_mape
})


# =========================================================
# MODEL 3 — LOWEST AIC SARIMA
# SARIMA(0,1,2)(0,1,1,12)
# =========================================================

print("\n" + "=" * 70)
print("3. LOWEST-AIC SARIMA")
print("=" * 70)

lowest_aic_order = (0, 1, 2)
lowest_aic_seasonal_order = (0, 1, 1, 12)

lowest_aic_model = SARIMAX(
    y_train,
    order=lowest_aic_order,
    seasonal_order=lowest_aic_seasonal_order,
    enforce_stationarity=False,
    enforce_invertibility=False
)

lowest_aic_fit = lowest_aic_model.fit(
    disp=False
)

lowest_aic_forecast = lowest_aic_fit.forecast(
    TEST_SIZE
)

lowest_aic_mae, lowest_aic_rmse, lowest_aic_mape = calculate_metrics(
    y_test,
    lowest_aic_forecast
)

print(f"Order: {lowest_aic_order}")
print(f"Seasonal order: {lowest_aic_seasonal_order}")
print(f"MAE:  {lowest_aic_mae:.6f}")
print(f"RMSE: {lowest_aic_rmse:.6f}")
print(f"MAPE: {lowest_aic_mape:.6f}%")
print(f"AIC:  {lowest_aic_fit.aic:.6f}")


results.append({
    "model": "Lowest-AIC SARIMA",
    "order": str(lowest_aic_order),
    "seasonal_order": str(lowest_aic_seasonal_order),
    "MAE": lowest_aic_mae,
    "RMSE": lowest_aic_rmse,
    "MAPE": lowest_aic_mape
})


# =========================================================
# MODEL 4 — SECOND AIC SARIMA
# SARIMA(1,1,2)(0,1,1,12)
# =========================================================

print("\n" + "=" * 70)
print("4. SECOND-AIC SARIMA")
print("=" * 70)

second_aic_order = (1, 1, 2)
second_aic_seasonal_order = (0, 1, 1, 12)

second_aic_model = SARIMAX(
    y_train,
    order=second_aic_order,
    seasonal_order=second_aic_seasonal_order,
    enforce_stationarity=False,
    enforce_invertibility=False
)

second_aic_fit = second_aic_model.fit(
    disp=False
)

second_aic_forecast = second_aic_fit.forecast(
    TEST_SIZE
)

second_aic_mae, second_aic_rmse, second_aic_mape = calculate_metrics(
    y_test,
    second_aic_forecast
)

print(f"Order: {second_aic_order}")
print(f"Seasonal order: {second_aic_seasonal_order}")
print(f"MAE:  {second_aic_mae:.6f}")
print(f"RMSE: {second_aic_rmse:.6f}")
print(f"MAPE: {second_aic_mape:.6f}%")
print(f"AIC:  {second_aic_fit.aic:.6f}")


results.append({
    "model": "Second-AIC SARIMA",
    "order": str(second_aic_order),
    "seasonal_order": str(second_aic_seasonal_order),
    "MAE": second_aic_mae,
    "RMSE": second_aic_rmse,
    "MAPE": second_aic_mape
})


# =========================================================
# SAVE RESULTS
# =========================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# DISPLAY FINAL COMPARISON
# =========================================================

print("\n" + "=" * 70)
print("FINAL BASELINE COMPARISON")
print("=" * 70)

print(
    results_df[
        [
            "model",
            "MAE",
            "RMSE",
            "MAPE"
        ]
    ].to_string(index=False)
)

print("\nResults saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)
print("FINAL EVALUATION COMPLETED")
print("=" * 70)