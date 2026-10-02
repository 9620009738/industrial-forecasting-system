from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORECAST_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "forecasts"
)

OUTPUT_DIR = FORECAST_DIR


def calculate_mape(actual, predicted):
    """
    Calculate Mean Absolute Percentage Error.
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


def evaluate_forecast_file(file_path, model_name):
    """
    Calculate evaluation metrics from a forecast CSV.
    """

    df = pd.read_csv(file_path)

    actual = df["actual"]
    predicted = df["forecast"]

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

    mape = calculate_mape(
        actual,
        predicted
    )

    return {
        "Model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "MAPE (%)": mape
    }


def main():

    print("=" * 60)
    print("BASELINE MODEL COMPARISON")
    print("=" * 60)

    tesm_file = (
        FORECAST_DIR
        / "tesm_baseline_forecast.csv"
    )

    sarima_file = (
        FORECAST_DIR
        / "sarima_baseline_forecast.csv"
    )

    results = []

    results.append(
        evaluate_forecast_file(
            tesm_file,
            "TESM"
        )
    )

    results.append(
        evaluate_forecast_file(
            sarima_file,
            "SARIMA"
        )
    )

    comparison = pd.DataFrame(
        results
    )

    print("\nBaseline evaluation results:")

    print(
        comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}"
        )
    )

    output_file = (
        OUTPUT_DIR
        / "baseline_model_comparison.csv"
    )

    comparison.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nComparison saved to:\n"
        f"{output_file}"
    )

    print("\n" + "=" * 60)
    print("BASELINE COMPARISON COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()