import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error


warnings.filterwarnings("ignore")


INPUT_FILE = Path(
    "data/processed/iip_food_products_with_cpi_2013_2025.csv"
)

OUTPUT_DIR = Path("outputs/forecasts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("MATCHED WALK-FORWARD: SARIMA vs SARIMAX + FORECASTED CPI")
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


# ---------------------------------------------------------
# 2. Development data
# ---------------------------------------------------------

development = df[
    df["date"] <= pd.Timestamp("2024-03-01")
].copy()

print("\nDevelopment observations:", len(development))

print(
    "Development period:",
    development["date"].min(),
    "→",
    development["date"].max()
)


# ---------------------------------------------------------
# 3. Matched origins
# ---------------------------------------------------------
#
# Both models will use exactly these origins:
#
# 96  -> 12-month forecast
# 108 -> 12-month forecast
# 120 -> 12-month forecast
#
# No origin 132 because the development dataset has
# only 3 observations after January 2024.
# ---------------------------------------------------------

origins = [96, 108, 120]

horizon = 12

results = []


# ---------------------------------------------------------
# 4. Walk-forward evaluation
# ---------------------------------------------------------

for origin in origins:

    print("\n" + "=" * 70)
    print(f"ORIGIN: {origin}")
    print("=" * 70)

    train = development.iloc[:origin].copy()

    test = development.iloc[
        origin:origin + horizon
    ].copy()

    print(
        "\nTraining:",
        train["date"].min(),
        "→",
        train["date"].max()
    )

    print(
        "Forecast:",
        test["date"].min(),
        "→",
        test["date"].max()
    )


    # =====================================================
    # MODEL 1 — SARIMA
    # =====================================================

    print("\nFitting SARIMA...")

    y_train = train["index"]
    y_test = test["index"]

    sarima_model = SARIMAX(
        y_train,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    sarima_fit = sarima_model.fit(
        disp=False
    )

    sarima_forecast = sarima_fit.get_forecast(
        steps=horizon
    ).predicted_mean.to_numpy()


    sarima_mae = mean_absolute_error(
        y_test,
        sarima_forecast
    )

    sarima_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            sarima_forecast
        )
    )

    sarima_mape = np.mean(
        np.abs(
            (y_test.to_numpy() - sarima_forecast)
            / y_test.to_numpy()
        )
    ) * 100


    print(
        f"SARIMA MAE:  {sarima_mae:.6f}"
    )

    print(
        f"SARIMA RMSE: {sarima_rmse:.6f}"
    )

    print(
        f"SARIMA MAPE: {sarima_mape:.6f}%"
    )


    # =====================================================
    # MODEL 2 — FORECAST CPI
    # =====================================================

    print("\nForecasting CPI...")

    cpi_model = ExponentialSmoothing(
        train["cpi_general_combined"],
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated"
    )

    cpi_fit = cpi_model.fit(
        optimized=True
    )

    cpi_forecast = cpi_fit.forecast(
        horizon
    )

    cpi_forecast = np.asarray(
        cpi_forecast
    )


    # =====================================================
    # MODEL 3 — SARIMAX + FORECASTED CPI
    # =====================================================

    print("Fitting SARIMAX...")

    exog_train = train[
        ["cpi_general_combined"]
    ]

    exog_future = pd.DataFrame({
        "cpi_general_combined":
            cpi_forecast
    })

    sarimax_model = SARIMAX(
        y_train,
        exog=exog_train,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    sarimax_fit = sarimax_model.fit(
        disp=False
    )

    sarimax_forecast = (
        sarimax_fit
        .get_forecast(
            steps=horizon,
            exog=exog_future
        )
        .predicted_mean
        .to_numpy()
    )


    sarimax_mae = mean_absolute_error(
        y_test,
        sarimax_forecast
    )

    sarimax_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            sarimax_forecast
        )
    )

    sarimax_mape = np.mean(
        np.abs(
            (y_test.to_numpy() - sarimax_forecast)
            / y_test.to_numpy()
        )
    ) * 100


    print(
        f"SARIMAX MAE:  {sarimax_mae:.6f}"
    )

    print(
        f"SARIMAX RMSE: {sarimax_rmse:.6f}"
    )

    print(
        f"SARIMAX MAPE: {sarimax_mape:.6f}%"
    )


    # =====================================================
    # Store results
    # =====================================================

    results.append({
        "origin": origin,

        "train_start": train["date"].min(),
        "train_end": train["date"].max(),

        "test_start": test["date"].min(),
        "test_end": test["date"].max(),

        "sarima_mae": sarima_mae,
        "sarima_rmse": sarima_rmse,
        "sarima_mape": sarima_mape,

        "sarimax_mae": sarimax_mae,
        "sarimax_rmse": sarimax_rmse,
        "sarimax_mape": sarimax_mape
    })


# ---------------------------------------------------------
# 5. Results dataframe
# ---------------------------------------------------------

results_df = pd.DataFrame(results)


# ---------------------------------------------------------
# 6. Average metrics
# ---------------------------------------------------------

summary = pd.DataFrame({
    "model": [
        "SARIMA",
        "SARIMAX_forecasted_CPI"
    ],

    "average_mae": [
        results_df["sarima_mae"].mean(),
        results_df["sarimax_mae"].mean()
    ],

    "average_rmse": [
        results_df["sarima_rmse"].mean(),
        results_df["sarimax_rmse"].mean()
    ],

    "average_mape": [
        results_df["sarima_mape"].mean(),
        results_df["sarimax_mape"].mean()
    ],

    "origins_evaluated": [
        len(results_df),
        len(results_df)
    ]
})


# ---------------------------------------------------------
# 7. Save results
# ---------------------------------------------------------

results_file = (
    OUTPUT_DIR /
    "matched_walk_forward_sarima_sarimax.csv"
)

summary_file = (
    OUTPUT_DIR /
    "matched_walk_forward_sarima_sarimax_summary.csv"
)

results_df.to_csv(
    results_file,
    index=False
)

summary.to_csv(
    summary_file,
    index=False
)


# ---------------------------------------------------------
# 8. Print results
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("MATCHED WALK-FORWARD RESULTS")
print("=" * 70)

print(
    results_df[
        [
            "origin",
            "sarima_mae",
            "sarima_rmse",
            "sarima_mape",
            "sarimax_mae",
            "sarimax_rmse",
            "sarimax_mape"
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 70)
print("AVERAGE RESULTS")
print("=" * 70)

print(summary.to_string(index=False))


print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(results_file)
print(summary_file)


print("\nMATCHED WALK-FORWARD COMPARISON COMPLETE.")