from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error


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


SEASONAL_PERIOD = 12

CANDIDATES = [
    {
        "name": "Paper SARIMA",
        "order": (1, 1, 1),
        "seasonal_order": (1, 1, 1, 12)
    },
    {
        "name": "Lowest AIC SARIMA",
        "order": (0, 1, 2),
        "seasonal_order": (0, 1, 1, 12)
    },
    {
        "name": "Second AIC SARIMA",
        "order": (1, 1, 2),
        "seasonal_order": (0, 1, 1, 12)
    }
]


def calculate_mape(actual, predicted):
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


def load_data():

    df = pd.read_csv(DATA_FILE)

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    return df


def fit_and_forecast(
    train_series,
    steps,
    order,
    seasonal_order
):

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore"
        )

        model = SARIMAX(
            train_series,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        fitted_model = model.fit(
            disp=False
        )

    forecast = fitted_model.forecast(
        steps=steps
    )

    return np.asarray(forecast)


def main():

    print("=" * 60)
    print("WALK-FORWARD SARIMA VALIDATION")
    print("=" * 60)

    df = load_data()

    # Keep the final 12 months untouched.
    development_data = df.iloc[:-12].copy()

    print("\nDevelopment dataset:")
    print(
        f"{development_data['date'].min().date()} "
        f"to "
        f"{development_data['date'].max().date()}"
    )

    print(
        f"Observations: "
        f"{len(development_data)}"
    )

    # Use 12-month forecast horizons.
    forecast_horizon = 12

    # Historical origins.
    origins = [
        96,
        108,
        120,
        132
    ]

    print("\nWalk-forward origins:")

    for origin in origins:
        print(
            f"Origin {origin}: "
            f"training through "
            f"{development_data.iloc[origin - 1]['date'].date()}"
        )

    results = []

    for candidate in CANDIDATES:

        print("\n" + "-" * 60)
        print(
            f"Evaluating: "
            f"{candidate['name']}"
        )
        print(
            f"Order: "
            f"{candidate['order']}"
        )
        print(
            f"Seasonal order: "
            f"{candidate['seasonal_order']}"
        )
        print("-" * 60)

        for origin in origins:

            train = development_data.iloc[
                :origin
            ]

            validation = development_data.iloc[
                origin:origin + forecast_horizon
            ]

            if len(validation) < forecast_horizon:
                continue

            train_series = (
                train
                .set_index("date")["index"]
            )

            actual = validation["index"].values

            forecast = fit_and_forecast(
                train_series=train_series,
                steps=forecast_horizon,
                order=candidate["order"],
                seasonal_order=candidate[
                    "seasonal_order"
                ]
            )

            mae = mean_absolute_error(
                actual,
                forecast
            )

            rmse = np.sqrt(
                mean_squared_error(
                    actual,
                    forecast
                )
            )

            mape = calculate_mape(
                actual,
                forecast
            )

            results.append({
                "model": candidate["name"],
                "order": str(
                    candidate["order"]
                ),
                "seasonal_order": str(
                    candidate["seasonal_order"]
                ),
                "origin_observations": origin,
                "validation_start":
                    validation["date"].min(),
                "validation_end":
                    validation["date"].max(),
                "MAE": mae,
                "RMSE": rmse,
                "MAPE (%)": mape
            })

            print(
                f"Origin {origin}: "
                f"MAE={mae:.4f}, "
                f"RMSE={rmse:.4f}, "
                f"MAPE={mape:.4f}%"
            )

    results_df = pd.DataFrame(
        results
    )

    summary = (
        results_df
        .groupby(
            [
                "model",
                "order",
                "seasonal_order"
            ]
        )
        [
            [
                "MAE",
                "RMSE",
                "MAPE (%)"
            ]
        ]
        .mean()
        .reset_index()
    )

    summary = summary.sort_values(
        "RMSE"
    ).reset_index(
        drop=True
    )

    print("\n" + "=" * 60)
    print("WALK-FORWARD SUMMARY")
    print("=" * 60)

    print(
        summary.to_string(
            index=False,
            float_format=lambda x:
            f"{x:.6f}"
        )
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results_file = (
        OUTPUT_DIR
        / "sarima_walk_forward_results.csv"
    )

    summary_file = (
        OUTPUT_DIR
        / "sarima_walk_forward_summary.csv"
    )

    results_df.to_csv(
        results_file,
        index=False
    )

    summary.to_csv(
        summary_file,
        index=False
    )

    print(
        f"\nDetailed results saved to:\n"
        f"{results_file}"
    )

    print(
        f"\nSummary saved to:\n"
        f"{summary_file}"
    )

    print("\n" + "=" * 60)
    print("WALK-FORWARD VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()