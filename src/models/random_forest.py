from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "iip_food_products_ml_features.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "target"

FEATURES = [
    "month_number",
    "quarter",
    "year_number",
    "month_sin",
    "month_cos",
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_6",
    "lag_12",
    "rolling_mean_3",
    "rolling_std_3",
    "rolling_mean_6",
    "rolling_std_6",
    "rolling_mean_12",
    "rolling_std_12",
]

# Final untouched test period
FINAL_TEST_START = pd.Timestamp("2024-04-01")

# Historical walk-forward validation periods
VALIDATION_PERIODS = {
    2021: pd.date_range("2021-01-01", "2021-12-01", freq="MS"),
    2022: pd.date_range("2022-01-01", "2022-12-01", freq="MS"),
    2023: pd.date_range("2023-01-01", "2023-12-01", freq="MS"),
}


# ============================================================
# METRICS
# ============================================================

def calculate_mape(actual, predicted):
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    mask = actual != 0

    return (
        np.mean(
            np.abs(
                (actual[mask] - predicted[mask])
                / actual[mask]
            )
        )
        * 100
    )


def calculate_metrics(actual, predicted):
    return {
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "MAPE": calculate_mape(actual, predicted),
    }


# ============================================================
# FEATURE CONSTRUCTION FOR FUTURE FORECASTING
# ============================================================

def build_future_features(history, forecast_date):
    """
    Construct one future feature row using only information
    available before forecast_date.

    history:
        Series indexed by date containing historical actual values
        and previously generated forecasts.

    forecast_date:
        Month being forecast.
    """

    month = forecast_date.month
    quarter = forecast_date.quarter

    # Calendar features
    month_sin = np.sin(2 * np.pi * month / 12)
    month_cos = np.cos(2 * np.pi * month / 12)

    # Year number
    year_number = forecast_date.year

    # Historical target values
    lag_1 = history.iloc[-1]
    lag_2 = history.iloc[-2]
    lag_3 = history.iloc[-3]
    lag_6 = history.iloc[-6]
    lag_12 = history.iloc[-12]

    # Rolling statistics must use history BEFORE
    # the month being forecast.
    rolling_mean_3 = history.iloc[-3:].mean()
    rolling_std_3 = history.iloc[-3:].std()

    rolling_mean_6 = history.iloc[-6:].mean()
    rolling_std_6 = history.iloc[-6:].std()

    rolling_mean_12 = history.iloc[-12:].mean()
    rolling_std_12 = history.iloc[-12:].std()

    features = {
        "month_number": month,
        "quarter": quarter,
        "year_number": year_number,
        "month_sin": month_sin,
        "month_cos": month_cos,
        "lag_1": lag_1,
        "lag_2": lag_2,
        "lag_3": lag_3,
        "lag_6": lag_6,
        "lag_12": lag_12,
        "rolling_mean_3": rolling_mean_3,
        "rolling_std_3": rolling_std_3,
        "rolling_mean_6": rolling_mean_6,
        "rolling_std_6": rolling_std_6,
        "rolling_mean_12": rolling_mean_12,
        "rolling_std_12": rolling_std_12,
    }

    return pd.DataFrame([features], columns=FEATURES)


# ============================================================
# RECURSIVE FORECAST
# ============================================================

def recursive_forecast(model, training_df, forecast_dates):
    """
    Generate a multi-step forecast recursively.

    After each prediction, that prediction is added to history
    and becomes available for constructing the next month's
    lag/rolling features.
    """

    history = training_df.set_index("date")[TARGET].copy()

    predictions = []

    for forecast_date in forecast_dates:

        X_future = build_future_features(
            history,
            forecast_date
        )

        prediction = model.predict(X_future)[0]

        predictions.append(prediction)

        # Add prediction to history so it can be used
        # for the next forecast month.
        history.loc[forecast_date] = prediction

    return np.array(predictions)


# ============================================================
# TRAIN + VALIDATE
# ============================================================

def run_validation_period(df, year, forecast_dates):

    forecast_start = forecast_dates[0]

    training_df = df[df["date"] < forecast_start].copy()

    validation_df = df[
        df["date"].isin(forecast_dates)
    ].copy()

    X_train = training_df[FEATURES]
    y_train = training_df[TARGET]

    actual = validation_df[TARGET].to_numpy()

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features=1.0,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predicted = recursive_forecast(
        model,
        training_df,
        forecast_dates,
    )

    metrics = calculate_metrics(
        actual,
        predicted,
    )

    result = pd.DataFrame({
        "date": forecast_dates,
        "actual": actual,
        "forecast": predicted,
        "period": year,
    })

    return model, result, metrics


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("RANDOM FOREST — LEAKAGE-SAFE TIME-SERIES FORECASTING")
    print("=" * 70)

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = pd.read_csv(DATA_FILE)

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    print("\nDataset:")
    print(f"Rows: {len(df)}")
    print(
        f"Date range: {df['date'].min()} → "
        f"{df['date'].max()}"
    )

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    missing_features = df[FEATURES].isna().sum().sum()

    duplicate_dates = df["date"].duplicated().sum()

    print("\nFeature validation:")
    print(
        f"Missing feature values: {missing_features}"
    )
    print(
        f"Duplicate dates: {duplicate_dates}"
    )

    if missing_features != 0:
        raise ValueError(
            "Missing values detected in ML features."
        )

    if duplicate_dates != 0:
        raise ValueError(
            "Duplicate dates detected."
        )

    # --------------------------------------------------------
    # WALK-FORWARD VALIDATION
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("WALK-FORWARD VALIDATION")
    print("=" * 70)

    validation_results = []
    validation_metrics = []

    for year, forecast_dates in VALIDATION_PERIODS.items():

        print(f"\n--- Validation Year: {year} ---")

        model, result, metrics = run_validation_period(
            df,
            year,
            forecast_dates,
        )

        training_rows = (
            df["date"] < forecast_dates[0]
        ).sum()

        print(
            f"Training rows: {training_rows}"
        )

        print(
            f"Validation period: "
            f"{forecast_dates[0].strftime('%Y-%m')} → "
            f"{forecast_dates[-1].strftime('%Y-%m')}"
        )

        print(
            f"MAE  : {metrics['MAE']:.6f}"
        )
        print(
            f"RMSE : {metrics['RMSE']:.6f}"
        )
        print(
            f"MAPE : {metrics['MAPE']:.6f}%"
        )

        validation_results.append(result)

        validation_metrics.append({
            "period": year,
            "train_rows": training_rows,
            "validation_rows": len(forecast_dates),
            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "MAPE": metrics["MAPE"],
        })

    # --------------------------------------------------------
    # SAVE VALIDATION RESULTS
    # --------------------------------------------------------

    validation_forecasts = pd.concat(
        validation_results,
        ignore_index=True,
    )

    validation_metrics_df = pd.DataFrame(
        validation_metrics
    )

    validation_forecasts.to_csv(
        OUTPUT_DIR / "random_forest_walk_forward_forecasts.csv",
        index=False,
    )

    validation_metrics_df.to_csv(
        OUTPUT_DIR / "random_forest_walk_forward_metrics.csv",
        index=False,
    )

    # --------------------------------------------------------
    # FINAL TEST
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL UNTOUCHED TEST")
    print("=" * 70)

    development_df = df[
        df["date"] < FINAL_TEST_START
    ].copy()

    final_test_df = df[
        df["date"] >= FINAL_TEST_START
    ].copy()

    final_dates = final_test_df["date"].tolist()

    X_train = development_df[FEATURES]
    y_train = development_df[TARGET]

    final_model = RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features=1.0,
        random_state=42,
        n_jobs=-1,
    )

    final_model.fit(
        X_train,
        y_train,
    )
    final_model = RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features=1.0,
        random_state=42,
        n_jobs=-1,
    )

    final_model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # SAVE TRAINED FINAL MODEL
    # --------------------------------------------------------

    import joblib

    model_path = PROJECT_ROOT / "models" / "random_forest_food_products.joblib"

    joblib.dump(
        final_model,
        model_path
    )

    print(
        f"Saved trained model: {model_path}"
    )

    final_predictions = recursive_forecast(
        final_model,
        development_df,
        final_dates,
    )

    final_predictions = recursive_forecast(
        final_model,
        development_df,
        final_dates,
    )

    final_actual = final_test_df[TARGET].to_numpy()

    final_metrics = calculate_metrics(
        final_actual,
        final_predictions,
    )

    print(
        f"Training period: "
        f"{development_df['date'].min()} → "
        f"{development_df['date'].max()}"
    )

    print(
        f"Final test period: "
        f"{final_test_df['date'].min()} → "
        f"{final_test_df['date'].max()}"
    )

    print(
        f"\nMAE  : {final_metrics['MAE']:.6f}"
    )

    print(
        f"RMSE : {final_metrics['RMSE']:.6f}"
    )

    print(
        f"MAPE : {final_metrics['MAPE']:.6f}%"
    )

    # --------------------------------------------------------
    # SAVE FINAL FORECAST
    # --------------------------------------------------------

    final_forecast_df = pd.DataFrame({
        "date": final_dates,
        "actual": final_actual,
        "forecast": final_predictions,
    })

    final_forecast_df.to_csv(
        OUTPUT_DIR / "random_forest_final_forecast.csv",
        index=False,
    )

    final_metrics_df = pd.DataFrame([{
        "model": "Random Forest",
        "train_start": development_df["date"].min(),
        "train_end": development_df["date"].max(),
        "test_start": final_test_df["date"].min(),
        "test_end": final_test_df["date"].max(),
        "test_rows": len(final_test_df),
        "MAE": final_metrics["MAE"],
        "RMSE": final_metrics["RMSE"],
        "MAPE": final_metrics["MAPE"],
    }])

    final_metrics_df.to_csv(
        OUTPUT_DIR / "random_forest_final_metrics.csv",
        index=False,
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RANDOM FOREST VALIDATION COMPLETED")
    print("=" * 70)

    print("\nFiles created:")

    print(
        "1.",
        OUTPUT_DIR
        / "random_forest_walk_forward_forecasts.csv"
    )

    print(
        "2.",
        OUTPUT_DIR
        / "random_forest_walk_forward_metrics.csv"
    )

    print(
        "3.",
        OUTPUT_DIR
        / "random_forest_final_forecast.csv"
    )

    print(
        "4.",
        OUTPUT_DIR
        / "random_forest_final_metrics.csv"
    )


if __name__ == "__main__":
    main()