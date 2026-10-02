import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error


INPUT_FILE = Path(
    "data/processed/iip_food_products_with_cpi_2013_2025.csv"
)

OUTPUT_DIR = Path("outputs/forecasts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("SARIMAX WITH CPI — EX-POST CONTROLLED EXPERIMENT")
print("=" * 70)


# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)


# ---------------------------------------------------------
# 2. Train / test split
# ---------------------------------------------------------

train_end = pd.Timestamp("2024-03-01")
test_start = pd.Timestamp("2024-04-01")
test_end = pd.Timestamp("2025-03-01")

train = df[df["date"] <= train_end].copy()

test = df[
    (df["date"] >= test_start) &
    (df["date"] <= test_end)
].copy()


y_train = train["index"]

y_test = test["index"]

exog_train = train[["cpi_general_combined"]]

exog_test = test[["cpi_general_combined"]]


print("\nTraining observations:", len(train))
print("Testing observations:", len(test))

print(
    "\nTraining period:",
    train["date"].min(),
    "→",
    train["date"].max()
)

print(
    "Testing period:",
    test["date"].min(),
    "→",
    test["date"].max()
)


# ---------------------------------------------------------
# 3. Fit SARIMAX
# ---------------------------------------------------------
#
# Same SARIMA structure as the paper baseline:
#
# (1,1,1)(1,1,1,12)
#
# CPI is supplied as an exogenous variable.
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("FITTING SARIMAX")
print("=" * 70)

model = SARIMAX(
    y_train,
    exog=exog_train,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12),
    enforce_stationarity=False,
    enforce_invertibility=False
)

results = model.fit(disp=False)

print("\nSARIMAX fitted successfully.")

print(f"AIC: {results.aic:.6f}")
print(f"BIC: {results.bic:.6f}")


# ---------------------------------------------------------
# 4. Forecast test period
# ---------------------------------------------------------

forecast = results.get_forecast(
    steps=len(test),
    exog=exog_test
)

forecast_mean = forecast.predicted_mean

forecast_ci = forecast.conf_int()


# ---------------------------------------------------------
# 5. Evaluation
# ---------------------------------------------------------

actual = y_test.to_numpy()
predicted = forecast_mean.to_numpy()

mae = mean_absolute_error(
    actual,
    predicted
)

rmse = np.sqrt(
    mean_squared_error(
        actual,
        predicted
    )
)

mape = np.mean(
    np.abs(
        (actual - predicted) / actual
    )
) * 100


print("\n" + "=" * 70)
print("SARIMAX TEST RESULTS")
print("=" * 70)

print(f"MAE:  {mae:.6f}")
print(f"RMSE: {rmse:.6f}")
print(f"MAPE: {mape:.6f}%")


# ---------------------------------------------------------
# 6. Create forecast table
# ---------------------------------------------------------

forecast_df = pd.DataFrame({
    "date": test["date"].values,
    "actual_iip": actual,
    "sarimax_forecast": predicted,
    "cpi_actual": test[
        "cpi_general_combined"
    ].values
})

# Add confidence intervals
forecast_df["lower_ci"] = forecast_ci.iloc[:, 0].values
forecast_df["upper_ci"] = forecast_ci.iloc[:, 1].values


# ---------------------------------------------------------
# 7. Save forecast
# ---------------------------------------------------------

forecast_file = (
    OUTPUT_DIR /
    "sarimax_cpi_expost_forecast.csv"
)

forecast_df.to_csv(
    forecast_file,
    index=False
)


# ---------------------------------------------------------
# 8. Save metrics
# ---------------------------------------------------------

metrics_df = pd.DataFrame({
    "model": ["SARIMAX_CPI_EXPOST"],
    "mae": [mae],
    "rmse": [rmse],
    "mape": [mape],
    "aic": [results.aic],
    "bic": [results.bic],
    "train_start": [train["date"].min()],
    "train_end": [train["date"].max()],
    "test_start": [test["date"].min()],
    "test_end": [test["date"].max()],
    "test_observations": [len(test)]
})

metrics_file = (
    OUTPUT_DIR /
    "sarimax_cpi_expost_metrics.csv"
)

metrics_df.to_csv(
    metrics_file,
    index=False
)


# ---------------------------------------------------------
# 9. Print forecast
# ---------------------------------------------------------

print("\nForecasts:")

print(
    forecast_df[
        [
            "date",
            "actual_iip",
            "sarimax_forecast",
            "cpi_actual"
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(forecast_file)
print(metrics_file)

print("\nSARIMAX EX-POST EXPERIMENT COMPLETE.")