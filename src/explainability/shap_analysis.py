from pathlib import Path
import xgboost
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "iip_food_products_ml_features.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "explainability"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FEATURES
# ============================================================

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


# ============================================================
# LOAD DATA
# ============================================================

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


# ============================================================
# LOAD MODELS
# ============================================================

def load_models():

    rf_path = (
        MODEL_DIR
        / "random_forest_food_products.joblib"
    )

    xgb_path = (
        MODEL_DIR
        / "xgboost_food_products.joblib"
    )

    rf_model = joblib.load(
        rf_path
    )

    xgb_model = joblib.load(
        xgb_path
    )

    return rf_model, xgb_model


# ============================================================
# CREATE EXPLAINABILITY DATASET
# ============================================================

def prepare_data(df):

    X = df[FEATURES].copy()

    return X


# ============================================================
# RANDOM FOREST SHAP
# ============================================================

def explain_random_forest(
    model,
    X
):

    print(
        "\nGenerating Random Forest SHAP values..."
    )

    explainer = shap.TreeExplainer(
        model
    )

    shap_values = explainer.shap_values(
        X
    )

    # Global feature importance
    importance = np.abs(
        shap_values
    ).mean(axis=0)

    importance_df = pd.DataFrame({
        "feature": FEATURES,
        "mean_absolute_shap": importance
    })

    importance_df = (
        importance_df
        .sort_values(
            "mean_absolute_shap",
            ascending=False
        )
        .reset_index(drop=True)
    )

    importance_df.to_csv(
        OUTPUT_DIR
        / "random_forest_shap_importance.csv",
        index=False
    )

    # Bar plot
    plt.figure(
        figsize=(10, 7)
    )

    shap.summary_plot(
        shap_values,
        X,
        plot_type="bar",
        show=False
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "random_forest_shap_summary_bar.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # Detailed SHAP summary
    plt.figure(
        figsize=(10, 7)
    )

    shap.summary_plot(
        shap_values,
        X,
        show=False
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "random_forest_shap_summary.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    return importance_df


# ============================================================
# XGBOOST SHAP
# ============================================================

def explain_xgboost(
    model,
    X
):

    print(
        "\nGenerating XGBoost SHAP values..."
    )

    # --------------------------------------------------------
    # XGBoost SHAP compatibility handling
    # --------------------------------------------------------

    try:

        explainer = shap.TreeExplainer(
            model
        )

        shap_values = explainer.shap_values(
            X
        )

    except ValueError as e:

        print(
            "\nStandard SHAP TreeExplainer failed for XGBoost."
        )

        print(
            f"Reason: {e}"
        )

        print(
            "\nTrying XGBoost native SHAP contribution method..."
        )

        booster = model.get_booster()

        dmatrix = xgboost.DMatrix(
            X,
            feature_names=FEATURES
        )

        shap_values_with_bias = booster.predict(
            dmatrix,
            pred_contribs=True
        )

        # Last column is the expected-value/base contribution.
        shap_values = shap_values_with_bias[:, :-1]

    # --------------------------------------------------------
    # GLOBAL FEATURE IMPORTANCE
    # --------------------------------------------------------

    importance = np.abs(
        shap_values
    ).mean(axis=0)

    importance_df = pd.DataFrame({
        "feature": FEATURES,
        "mean_absolute_shap": importance
    })

    importance_df = (
        importance_df
        .sort_values(
            "mean_absolute_shap",
            ascending=False
        )
        .reset_index(drop=True)
    )

    importance_df.to_csv(
        OUTPUT_DIR
        / "xgboost_shap_importance.csv",
        index=False
    )

    # --------------------------------------------------------
    # BAR PLOT
    # --------------------------------------------------------

    plt.figure(
        figsize=(10, 7)
    )

    shap.summary_plot(
        shap_values,
        X,
        plot_type="bar",
        show=False
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "xgboost_shap_summary_bar.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # --------------------------------------------------------
    # DETAILED SHAP SUMMARY
    # --------------------------------------------------------

    plt.figure(
        figsize=(10, 7)
    )

    shap.summary_plot(
        shap_values,
        X,
        show=False
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "xgboost_shap_summary.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    return importance_df

# ============================================================
# COMPARE MODEL FEATURE IMPORTANCE
# ============================================================

def create_comparison(
    rf_importance,
    xgb_importance
):

    comparison = rf_importance.merge(
        xgb_importance,
        on="feature",
        how="outer",
        suffixes=(
            "_random_forest",
            "_xgboost"
        )
    )

    comparison.to_csv(
        OUTPUT_DIR
        / "shap_feature_importance_comparison.csv",
        index=False
    )

    return comparison


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SHAP EXPLAINABILITY ANALYSIS")
    print("=" * 70)

    print("\nLoading dataset...")

    df = load_data()

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Date range: "
        f"{df['date'].min()} → "
        f"{df['date'].max()}"
    )

    print("\nPreparing features...")

    X = prepare_data(
        df
    )

    print(
        f"Feature rows: {len(X)}"
    )

    print(
        f"Feature count: {len(FEATURES)}"
    )

    print("\nLoading trained models...")

    rf_model, xgb_model = load_models()

    print(
        "Random Forest model loaded."
    )

    print(
        "XGBoost model loaded."
    )

    # --------------------------------------------------------
    # RANDOM FOREST
    # --------------------------------------------------------

    rf_importance = explain_random_forest(
        rf_model,
        X
    )

    # --------------------------------------------------------
    # XGBOOST
    # --------------------------------------------------------

    xgb_importance = explain_xgboost(
        xgb_model,
        X
    )

    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    comparison = create_comparison(
        rf_importance,
        xgb_importance
    )

    print(
        "\nTop Random Forest features:"
    )

    print(
        rf_importance.head(10)
    )

    print(
        "\nTop XGBoost features:"
    )

    print(
        xgb_importance.head(10)
    )

    print(
        "\nSHAP comparison:"
    )

    print(
        comparison.head(10)
    )

    print("\n" + "=" * 70)
    print("SHAP ANALYSIS COMPLETED")
    print("=" * 70)

    print(
        "\nOutput directory:"
    )

    print(
        OUTPUT_DIR
    )


if __name__ == "__main__":
    main()