from pathlib import Path

import pandas as pd
import numpy as np

from statsmodels.tsa.statespace.sarimax import SARIMAX
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


def train_sarima(train_series):
    """
    Train SARIMA(1,1,1)(1,1,1,12).
    """

    model = SARIMAX(
        train_series,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    fitted_model = model.fit(
        disp=False
    )

    return fitted_model


def evaluate_sarima(train, test):

    train_series = train.set_index("date")["index"]

    test_series = test.set_index("date")["index"]

    fitted_model = train_sarima(
        train_series
    )

    forecast_result = fitted_model.get_forecast(
        steps=len(test_series)
    )

    forecast = forecast_result.predicted_mean

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

    aic = fitted_model.aic

    print("\n" + "=" * 60)
    print("SARIMA BASELINE")
    print("=" * 60)

    print("\nModel configuration:")
    print("Order: (1, 1, 1)")
    print("Seasonal order: (1, 1, 1, 12)")
    print("Seasonal period: 12")

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
    print(f"AIC: {aic:.6f}")

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

    return (
        fitted_model,
        forecast_table,
        rmse,
        mape,
        aic
    )


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
        mape,
        aic
    ) = evaluate_sarima(
        train,
        test
    )

    output_file = (
        OUTPUT_DIR
        / "sarima_baseline_forecast.csv"
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
    print("SARIMA BASELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()