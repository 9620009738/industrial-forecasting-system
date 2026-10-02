import os
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = "outputs/metrics"
FORECAST_DIR = "outputs/forecasts"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# FINAL TEST RESULTS
# ============================================================

final_results = [
    {
        "model": "TESM",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 4.458551813300915,
        "RMSE": 6.103024476046267,
        "MAPE": 3.402380226103237,
        "AIC": None
    },
    {
        "model": "Paper SARIMA",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 5.015810781631096,
        "RMSE": 6.824236271496022,
        "MAPE": 3.811084363509445,
        "AIC": 763.682033
    },
    {
        "model": "Lowest-AIC SARIMA",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 4.820804037287314,
        "RMSE": 6.650211617132023,
        "MAPE": 3.6747266738309774,
        "AIC": 753.442834
    },
    {
        "model": "Second-AIC SARIMA",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 5.038403097872518,
        "RMSE": 6.831407418420929,
        "MAPE": 3.82716602561221,
        "AIC": None
    },
    {
        "model": "SARIMAX-CPI",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 5.259865,
        "RMSE": 6.845576,
        "MAPE": 3.979323,
        "AIC": 708.018899
    },
    {
        "model": "Random Forest",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 6.503566666666707,
        "RMSE": 8.689590101188122,
        "MAPE": 5.10276340113619,
        "AIC": None
    },
    {
        "model": "XGBoost",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 5.959216944376629,
        "RMSE": 7.368707110491003,
        "MAPE": 4.629179207470783,
        "AIC": None
    },
    {
        "model": "LSTM",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 7.016927,
        "RMSE": 9.360733,
        "MAPE": 5.454768,
        "AIC": None
    },
    {
        "model": "GRU",
        "evaluation_type": "Final Test",
        "period": "Apr 2024-Mar 2025",
        "MAE": 6.358302,
        "RMSE": 8.124222,
        "MAPE": 4.835500,
        "AIC": None
    }
]


# ============================================================
# WALK-FORWARD RESULTS
# ============================================================

walk_forward_results = [
    {
        "model": "Paper SARIMA",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 4.465328910464255,
        "RMSE": 5.634569558930418,
        "MAPE": 3.5885976361685774,
        "AIC": None
    },
    {
        "model": "Second-AIC SARIMA",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 4.585579135046421,
        "RMSE": 5.690190366441161,
        "MAPE": 3.670075117995533,
        "AIC": None
    },
    {
        "model": "Lowest-AIC SARIMA",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 5.225289182242406,
        "RMSE": 6.220274476603347,
        "MAPE": 4.1858064855298585,
        "AIC": None
    },
    {
        "model": "SARIMAX-CPI",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 4.424115,
        "RMSE": 5.838509,
        "MAPE": 3.400661,
        "AIC": None
    },
    {
        "model": "Random Forest",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 6.211794444444387,
        "RMSE": 7.803261782177175,
        "MAPE": 4.610166403341695,
        "AIC": None
    },
    {
        "model": "XGBoost",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 7.152592849731447,
        "RMSE": 8.778964640110024,
        "MAPE": 5.359814590744802,
        "AIC": None
    },
    {
        "model": "LSTM",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 6.283107,
        "RMSE": 7.744442,
        "MAPE": 4.748827,
        "AIC": None
    },
    {
        "model": "GRU",
        "evaluation_type": "Walk-Forward",
        "period": "2021-2023 average",
        "MAE": 7.307220,
        "RMSE": 8.534474,
        "MAPE": 5.577198,
        "AIC": None
    }
]


# ============================================================
# CREATE DATAFRAMES
# ============================================================

final_df = pd.DataFrame(final_results)

walk_df = pd.DataFrame(walk_forward_results)


# ============================================================
# SAVE COMPARISON TABLES
# ============================================================

final_path = (
    f"{OUTPUT_DIR}/model_comparison_final.csv"
)

walk_path = (
    f"{OUTPUT_DIR}/model_comparison_walk_forward.csv"
)

final_df.to_csv(
    final_path,
    index=False
)

walk_df.to_csv(
    walk_path,
    index=False
)


# ============================================================
# COMBINED TABLE
# ============================================================

combined_df = pd.concat(
    [final_df, walk_df],
    ignore_index=True
)

combined_path = (
    f"{OUTPUT_DIR}/model_comparison_all.csv"
)

combined_df.to_csv(
    combined_path,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("=" * 80)
print("FINAL TEST MODEL COMPARISON")
print("=" * 80)

print(
    final_df.to_string(index=False)
)

print("\n" + "=" * 80)
print("WALK-FORWARD MODEL COMPARISON")
print("=" * 80)

print(
    walk_df.to_string(index=False)
)


# ============================================================
# DATA VALIDATION
# ============================================================

expected_final_models = {
    "TESM",
    "Paper SARIMA",
    "Lowest-AIC SARIMA",
    "Second-AIC SARIMA",
    "SARIMAX-CPI",
    "Random Forest",
    "XGBoost",
    "LSTM",
    "GRU"
}

actual_final_models = set(
    final_df["model"]
)

if actual_final_models != expected_final_models:

    raise ValueError(
        "Final model comparison is missing or "
        "contains unexpected models."
    )


expected_ml_models = {
    "Random Forest",
    "XGBoost",
    "LSTM",
    "GRU"
}

actual_ml_models = set(
    final_df[
        final_df["model"].isin(expected_ml_models)
    ]["model"]
)

if actual_ml_models != expected_ml_models:

    raise ValueError(
        "One or more ML models are missing."
    )


# ============================================================
# COMPLETION
# ============================================================

print("\n" + "=" * 80)
print("SPRINT 10 COMPARISON TABLES CREATED")
print("=" * 80)

print("\nSaved:")
print(final_path)
print(walk_path)
print(combined_path)