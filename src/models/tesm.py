from pathlib import Path

import pandas as pd
import numpy as np

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "iip_food_products_baseline_2012_2025.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "forecasts"
)


def mean_absolute_percentage_error(actual, predicted):
    """
    Calculate MAPE while avoiding division by zero.
    """

    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    non_zero = actual != 0

    return (
        np.mean(
            np.abs(
                (actual[non_zero] - predicted[non_zero])
                / actual[non_zero]
            )
        )
        * 100
    )


def train_tesm(train_series):
    """
    Train Triple Exponential Smoothing
    using additive trend and additive seasonality.
    """

    model = ExponentialSmoothing(
        train_series,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated"
    )

    fitted_model = model.fit(
        optimized=True
    )

    return fitted_model


def evaluate_tesm(train, test):
    """
    Train TESM on the training data,
    forecast the test period,
    and calculate evaluation metrics.
    """

    train_series = train.set_index("date")["index"]

    test_series = test.set_index("date")["index"]

    fitted_model = train_tesm(train_series)

    forecast = fitted_model.forecast(
        len(test_series)
    )

    forecast = pd.Series(
        forecast,
        index=test_series.index,
        name="forecast"
    )

    rmse = np.sqrt(
        mean_squared_error(
            test_series,
            forecast
        )
    )

    mape = mean_absolute_percentage_error(
        test_series,
        forecast
    )

    print("\n" + "=" * 60)
    print("TESM / HOLT-WINTERS BASELINE")
    print("=" * 60)

    print("\nModel configuration:")
    print("Trend: additive")
    print("Seasonality: additive")
    print("Seasonal period: 12")
    print("Parameter optimization: enabled")

    print("\nTraining period:")
    print(
        f"{train['date'].min().date()} "
        f"to "
        f"{train['date'].max().date()}"
    )

    print(f"Training observations: {len(train)}")

    print("\nTesting period:")
    print(
        f"{test['date'].min().date()} "
        f"to "
        f"{test['date'].max().date()}"
    )

    print(f"Testing observations: {len(test)}")

    print("\nEvaluation metrics:")
    print(f"RMSE: {rmse:.6f}")
    print(f"MAPE: {mape:.6f}%")

    print("\nForecast values:")

    forecast_table = pd.DataFrame({
        "date": test_series.index,
        "actual": test_series.values,
        "forecast": forecast.values
    })

    forecast_table["error"] = (
        forecast_table["actual"]
        - forecast_table["forecast"]
    )

    print(
        forecast_table.to_string(
            index=False
        )
    )

    print("\nFitted smoothing parameters:")

    params = fitted_model.params

    for key in [
        "smoothing_level",
        "smoothing_trend",
        "smoothing_seasonal"
    ]:
        value = params.get(key)

        if value is not None:
            print(
                f"{key}: {value:.6f}"
            )

    return fitted_model, forecast_table, rmse, mape


def main():

    df = pd.read_csv(DATA_FILE)

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    test_size = 12

    train = df.iloc[:-test_size].copy()

    test = df.iloc[-test_size:].copy()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    (
        fitted_model,
        forecast_table,
        rmse,
        mape
    ) = evaluate_tesm(
        train,
        test
    )

    output_file = (
        OUTPUT_DIR
        / "tesm_baseline_forecast.csv"
    )

    forecast_table.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nForecast saved to:\n"
        f"{output_file}"
    )

    print("\n" + "=" * 60)
    print("TESM BASELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()