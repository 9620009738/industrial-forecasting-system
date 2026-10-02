from pathlib import Path
import warnings

import pandas as pd

from statsmodels.tsa.statespace.sarimax import SARIMAX


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


# Candidate non-seasonal orders.
P_VALUES = [0, 1, 2]
D_VALUES = [1]
Q_VALUES = [0, 1, 2]

# Candidate seasonal orders.
SEASONAL_P_VALUES = [0, 1]
SEASONAL_D_VALUES = [1]
SEASONAL_Q_VALUES = [0, 1]

SEASONAL_PERIOD = 12


def load_training_data():
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

    train_series = (
        train
        .set_index("date")["index"]
    )

    return train_series


def fit_candidate(
    series,
    order,
    seasonal_order
):
    """
    Fit one SARIMA candidate and return
    its information criteria.
    """

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore"
            )

            model = SARIMAX(
                series,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            fitted_model = model.fit(
                disp=False
            )

        return {
            "order": order,
            "seasonal_order": seasonal_order,
            "aic": fitted_model.aic,
            "bic": fitted_model.bic,
            "status": "success"
        }

    except Exception as error:

        return {
            "order": order,
            "seasonal_order": seasonal_order,
            "aic": None,
            "bic": None,
            "status": f"failed: {error}"
        }


def main():

    print("=" * 60)
    print("AUTOMATIC SARIMA CANDIDATE SEARCH")
    print("=" * 60)

    series = load_training_data()

    print("\nTraining observations:")
    print(len(series))

    print(
        f"Training period: "
        f"{series.index.min().date()} "
        f"to "
        f"{series.index.max().date()}"
    )

    print("\nCandidate search space:")

    print(
        f"Non-seasonal p: {P_VALUES}"
    )

    print(
        f"Non-seasonal d: {D_VALUES}"
    )

    print(
        f"Non-seasonal q: {Q_VALUES}"
    )

    print(
        f"Seasonal P: {SEASONAL_P_VALUES}"
    )

    print(
        f"Seasonal D: {SEASONAL_D_VALUES}"
    )

    print(
        f"Seasonal Q: {SEASONAL_Q_VALUES}"
    )

    print(
        f"Seasonal period: {SEASONAL_PERIOD}"
    )

    total_candidates = (
        len(P_VALUES)
        * len(D_VALUES)
        * len(Q_VALUES)
        * len(SEASONAL_P_VALUES)
        * len(SEASONAL_D_VALUES)
        * len(SEASONAL_Q_VALUES)
    )

    print(
        f"\nTotal candidates: "
        f"{total_candidates}"
    )

    results = []

    candidate_number = 0

    for p in P_VALUES:

        for d in D_VALUES:

            for q in Q_VALUES:

                order = (
                    p,
                    d,
                    q
                )

                for P in SEASONAL_P_VALUES:

                    for D in SEASONAL_D_VALUES:

                        for Q in SEASONAL_Q_VALUES:

                            seasonal_order = (
                                P,
                                D,
                                Q,
                                SEASONAL_PERIOD
                            )

                            candidate_number += 1

                            print(
                                f"\n[{candidate_number}/"
                                f"{total_candidates}] "
                                f"Testing "
                                f"SARIMA"
                                f"{order}"
                                f"{seasonal_order}"
                            )

                            result = fit_candidate(
                                series,
                                order,
                                seasonal_order
                            )

                            results.append(
                                result
                            )

    results_df = pd.DataFrame(
        results
    )

    successful_results = (
        results_df[
            results_df["status"]
            == "success"
        ]
        .copy()
    )

    successful_results = (
        successful_results
        .sort_values("aic")
        .reset_index(drop=True)
    )

    print("\n" + "=" * 60)
    print("SARIMA CANDIDATE RESULTS")
    print("=" * 60)

    print(
        successful_results[
            [
                "order",
                "seasonal_order",
                "aic",
                "bic"
            ]
        ].to_string(
            index=False
        )
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR
        / "sarima_candidate_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nCandidate results saved to:\n"
        f"{output_file}"
    )

    if len(successful_results) > 0:

        best_aic = (
            successful_results
            .iloc[0]
        )

        print("\nLowest-AIC candidate:")

        print(
            f"Order: "
            f"{best_aic['order']}"
        )

        print(
            f"Seasonal order: "
            f"{best_aic['seasonal_order']}"
        )

        print(
            f"AIC: "
            f"{best_aic['aic']:.6f}"
        )

        print(
            f"BIC: "
            f"{best_aic['bic']:.6f}"
        )

    print("\n" + "=" * 60)
    print("AUTOMATIC SARIMA SEARCH COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()