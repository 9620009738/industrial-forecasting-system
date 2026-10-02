from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD FINAL TEST RESULTS
# ============================================================

def load_final_test_results():

    results = []

    # --------------------------------------------------------
    # TESM + SARIMA + automatic SARIMA candidates
    # --------------------------------------------------------

    baseline_file = (
        OUTPUT_DIR / "final_baseline_evaluation.csv"
    )

    baseline = pd.read_csv(baseline_file)

    for _, row in baseline.iterrows():

        results.append({
            "model": row["model"],
            "evaluation_type": "Final Test",
            "period": "Apr 2024-Mar 2025",
            "MAE": row["MAE"],
            "RMSE": row["RMSE"],
            "MAPE": row["MAPE"],
            "AIC": None,
        })

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    rf_file = (
        OUTPUT_DIR / "random_forest_final_metrics.csv"
    )

    rf = pd.read_csv(rf_file)

    row = rf.iloc[0]

    results.append({
        "model": "Random Forest",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": row["MAE"],
        "RMSE": row["RMSE"],
        "MAPE": row["MAPE"],
        "AIC": None,
    })

    # --------------------------------------------------------
    # XGBoost
    # --------------------------------------------------------

    xgb_file = (
        OUTPUT_DIR / "xgboost_final_metrics.csv"
    )

    xgb = pd.read_csv(xgb_file)

    row = xgb.iloc[0]

    results.append({
        "model": "XGBoost",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": row["MAE"],
        "RMSE": row["RMSE"],
        "MAPE": row["MAPE"],
        "AIC": None,
    })

    return pd.DataFrame(results)


# ============================================================
# LOAD WALK-FORWARD RESULTS
# ============================================================

def load_walk_forward_results():

    results = []

    # --------------------------------------------------------
    # SARIMA
    # --------------------------------------------------------

    sarima_file = (
        OUTPUT_DIR / "sarima_walk_forward_summary.csv"
    )

    sarima = pd.read_csv(sarima_file)

    for _, row in sarima.iterrows():

        results.append({
            "model": row["model"],
            "evaluation_type": "Walk-Forward",
            "period": "2021-2023 average",
            "MAE": row["MAE"],
            "RMSE": row["RMSE"],
            "MAPE": row["MAPE (%)"],
        })

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    rf_file = (
        OUTPUT_DIR
        / "random_forest_walk_forward_metrics.csv"
    )

    rf = pd.read_csv(rf_file)

    results.append({
        "model": "Random Forest",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": rf["MAE"].mean(),
        "RMSE": rf["RMSE"].mean(),
        "MAPE": rf["MAPE"].mean(),
    })

    # --------------------------------------------------------
    # XGBoost
    # --------------------------------------------------------

    xgb_file = (
        OUTPUT_DIR
        / "xgboost_walk_forward_metrics.csv"
    )

    xgb = pd.read_csv(xgb_file)

    results.append({
        "model": "XGBoost",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": xgb["MAE"].mean(),
        "RMSE": xgb["RMSE"].mean(),
        "MAPE": xgb["MAPE"].mean(),
    })

    return pd.DataFrame(results)


# ============================================================
# VALIDATION AUDIT
# ============================================================

def validate_results(
    final_results,
    walk_forward_results,
):

    print("=" * 70)
    print("MODEL EVALUATION AUDIT")
    print("=" * 70)

    # --------------------------------------------------------
    # Final test checks
    # --------------------------------------------------------

    print("\nFINAL TEST CHECKS")

    expected_models = {
        "TESM",
        "Paper SARIMA",
        "Lowest-AIC SARIMA",
        "Second-AIC SARIMA",
        "Random Forest",
        "XGBoost",
    }

    actual_models = set(
        final_results["model"]
    )

    missing_models = (
        expected_models - actual_models
    )

    if missing_models:

        print(
            "Missing final-test models:",
            missing_models,
        )

    else:

        print(
            "All expected final-test models: PASS"
        )

    # --------------------------------------------------------
    # Final test period
    # --------------------------------------------------------

    periods = set(
        final_results["period"]
    )

    if periods == {"Apr 2024-Mar 2025"}:

        print(
            "Final test period consistency: PASS"
        )

    else:

        print(
            "Final test period consistency: FAIL"
        )

    # --------------------------------------------------------
    # Metric validation
    # --------------------------------------------------------

    metric_columns = [
        "MAE",
        "RMSE",
        "MAPE",
    ]

    if (
        final_results[metric_columns]
        .notna()
        .all()
        .all()
    ):

        print(
            "Final-test metrics complete: PASS"
        )

    else:

        print(
            "Final-test metrics complete: FAIL"
        )

    # --------------------------------------------------------
    # Walk-forward validation
    # --------------------------------------------------------

    print("\nWALK-FORWARD CHECKS")

    expected_walk_forward_models = {
        "Paper SARIMA",
        "Second AIC SARIMA",
        "Lowest AIC SARIMA",
        "Random Forest",
        "XGBoost",
    }

    actual_walk_forward_models = set(
        walk_forward_results["model"]
    )

    if (
        expected_walk_forward_models
        <= actual_walk_forward_models
    ):

        print(
            "Available walk-forward models: PASS"
        )

    else:

        print(
            "Available walk-forward models: CHECK"
        )

    if (
        walk_forward_results[
            "period"
        ].eq("2021-2023 average").all()
    ):

        print(
            "Walk-forward period labeling: PASS"
        )

    else:

        print(
            "Walk-forward period labeling: FAIL"
        )

    # --------------------------------------------------------
    # No automatic ranking
    # --------------------------------------------------------

    print(
        "\nScientific comparison rule:"
    )

    print(
        "No universal model ranking is generated."
    )

    print(
        "Metrics are reported descriptively."
    )

    print(
        "AIC is retained only for statistical models."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    final_results = load_final_test_results()

    walk_forward_results = (
        load_walk_forward_results()
    )

    validate_results(
        final_results,
        walk_forward_results,
    )

    # --------------------------------------------------------
    # Save final test table
    # --------------------------------------------------------

    final_output = (
        OUTPUT_DIR
        / "model_final_test_audit.csv"
    )

    final_results.to_csv(
        final_output,
        index=False,
    )

    # --------------------------------------------------------
    # Save walk-forward table
    # --------------------------------------------------------

    walk_output = (
        OUTPUT_DIR
        / "model_walk_forward_audit.csv"
    )

    walk_forward_results.to_csv(
        walk_output,
        index=False,
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL TEST AUDIT")
    print("=" * 70)

    print(
        final_results.to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)
    print("WALK-FORWARD AUDIT")
    print("=" * 70)

    print(
        walk_forward_results.to_string(
            index=False
        )
    )

    print("\nFiles created:")

    print(final_output)
    print(walk_output)

    print("\n" + "=" * 70)
    print("MODEL EVALUATION AUDIT COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()