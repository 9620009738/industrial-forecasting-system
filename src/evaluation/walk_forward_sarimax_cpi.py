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
print("REALISTIC WALK-FORWARD SARIMAX + FORECASTED CPI")
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
# 2. Development dataset
# ---------------------------------------------------------
#
# Keep the final 12 months completely untouched.
#
# Development:
# Jan 2013 → Mar 2024
#
# Final test:
# Apr 2024 → Mar 2025
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
# 3. Walk-forward origins
# ---------------------------------------------------------

origins = [96, 108, 120, 132]

horizon = 12

results = []


# ---------------------------------------------------------
# 4. Walk-forward loop
# ---------------------------------------------------------

for origin in origins:

    print("\n" + "=" * 70)
    print(f"ORIGIN: {origin}")
    print("=" * 70)

    train = development.iloc[:origin].copy()

    test = development.iloc[
        origin:origin + horizon
    ].copy()

    if len(test) < horizon:
        print(
            f"Skipping origin {origin}: "
            f"only {len(test)} test observations available."
        )
        continue

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


    # -----------------------------------------------------
    # 4A. Forecast CPI
    # -----------------------------------------------------

    print("\nForecasting CPI...")

    cpi_train = train[
        "cpi_general_combined"
    ]

    cpi_model = ExponentialSmoothing(
        cpi_train,
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

    print(
        "CPI forecast generated:",
        len(cpi_forecast),
        "months"
    )


    # -----------------------------------------------------
    # 4B. Fit SARIMAX
    # -----------------------------------------------------

    print("Fitting SARIMAX...")

    y_train = train["index"]

    y_test = test["index"]

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


    # -----------------------------------------------------
    # 4C. Forecast IIP
    # -----------------------------------------------------

    forecast = sarimax_fit.get_forecast(
        steps=horizon,
        exog=exog_future
    )

    iip_forecast = np.asarray(
        forecast.predicted_mean
    )

    actual = y_test.to_numpy()


    # -----------------------------------------------------
    # 4D. Metrics
    # -----------------------------------------------------

    mae = mean_absolute_error(
        actual,
        iip_forecast
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            iip_forecast
        )
    )

    mape = np.mean(
        np.abs(
            (actual - iip_forecast)
            / actual
        )
    ) * 100


    # -----------------------------------------------------
    # 4E. Store results
    # -----------------------------------------------------

    results.append({
        "origin_observations": origin,
        "train_start": train["date"].min(),
        "train_end": train["date"].max(),
        "test_start": test["date"].min(),
        "test_end": test["date"].max(),
        "test_observations": len(test),
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "sarimax_aic": sarimax_fit.aic
    })


    print(
        f"\nMAE:  {mae:.6f}"
    )

    print(
        f"RMSE: {rmse:.6f}"
    )

    print(
        f"MAPE: {mape:.6f}%"
    )


# ---------------------------------------------------------
# 5. Save detailed results
# ---------------------------------------------------------

results_df = pd.DataFrame(results)

results_file = (
    OUTPUT_DIR /
    "sarimax_cpi_walk_forward_results.csv"
)

results_df.to_csv(
    results_file,
    index=False
)


# ---------------------------------------------------------
# 6. Calculate average metrics
# ---------------------------------------------------------

if len(results_df) > 0:

    summary = pd.DataFrame({
        "model": [
            "SARIMAX_CPI_FORECASTED_EXOG"
        ],
        "average_mae": [
            results_df["mae"].mean()
        ],
        "average_rmse": [
            results_df["rmse"].mean()
        ],
        "average_mape": [
            results_df["mape"].mean()
        ],
        "origins_evaluated": [
            len(results_df)
        ]
    })

    summary_file = (
        OUTPUT_DIR /
        "sarimax_cpi_walk_forward_summary.csv"
    )

    summary.to_csv(
        summary_file,
        index=False
    )


    # -----------------------------------------------------
    # 7. Print summary
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("WALK-FORWARD SARIMAX SUMMARY")
    print("=" * 70)

    print(
        results_df[
            [
                "origin_observations",
                "mae",
                "rmse",
                "mape"
            ]
        ].to_string(index=False)
    )

    print("\nAverage MAE:")
    print(
        f"{results_df['mae'].mean():.6f}"
    )

    print("\nAverage RMSE:")
    print(
        f"{results_df['rmse'].mean():.6f}"
    )

    print("\nAverage MAPE:")
    print(
        f"{results_df['mape'].mean():.6f}%"
    )

    print("\nFiles saved:")
    print(results_file)
    print(summary_file)


print("\n" + "=" * 70)
print("WALK-FORWARD SARIMAX COMPLETE")
print("=" * 70)