import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

FEATURE_PATH = (
    "data/processed/"
    "iip_food_products_ml_features.csv"
)

OUTPUT_DIR = "outputs/explainability"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# LOAD FEATURES
# ============================================================

df = pd.read_csv(FEATURE_PATH)

df["date"] = pd.to_datetime(
    df["date"]
)

target_column = "target"

feature_columns = [
    column
    for column in df.columns
    if column not in ["date", target_column]
]

X = df[feature_columns]
y = df[target_column]


print("=" * 70)
print("FEATURE IMPORTANCE ANALYSIS")
print("=" * 70)

print("\nDataset shape:")
print(df.shape)

print("\nNumber of features:")
print(len(feature_columns))

print("\nFeatures:")
for feature in feature_columns:
    print("-", feature)


# ============================================================
# RANDOM FOREST
# ============================================================

print("\n" + "=" * 70)
print("RANDOM FOREST FEATURE IMPORTANCE")
print("=" * 70)

rf_model_path = (
    "models/random_forest_food_products.joblib"
)

if not os.path.exists(rf_model_path):

    raise FileNotFoundError(
        f"Random Forest model not found:\n"
        f"{rf_model_path}"
    )

rf_model = joblib.load(
    rf_model_path
)

rf_importance = pd.DataFrame({
    "feature": feature_columns,
    "importance": rf_model.feature_importances_
})

rf_importance = rf_importance.sort_values(
    "importance",
    ascending=False
).reset_index(drop=True)

print("\nRandom Forest feature importance:")
print(
    rf_importance.to_string(index=False)
)

rf_importance.to_csv(
    f"{OUTPUT_DIR}/random_forest_feature_importance.csv",
    index=False
)


# ============================================================
# RANDOM FOREST PLOT
# ============================================================

rf_plot = rf_importance.sort_values(
    "importance",
    ascending=True
)

plt.figure(figsize=(10, 8))

plt.barh(
    rf_plot["feature"],
    rf_plot["importance"]
)

plt.title(
    "Random Forest Feature Importance"
)

plt.xlabel(
    "Feature Importance"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/random_forest_feature_importance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# XGBOOST
# ============================================================

print("\n" + "=" * 70)
print("XGBOOST FEATURE IMPORTANCE")
print("=" * 70)

xgb_model_path = (
    "models/xgboost_food_products.json"
)

if not os.path.exists(xgb_model_path):

    raise FileNotFoundError(
        f"XGBoost model not found:\n"
        f"{xgb_model_path}"
    )

from xgboost import XGBRegressor

xgb_model = XGBRegressor()

xgb_model.load_model(
    xgb_model_path
)

xgb_importance = pd.DataFrame({
    "feature": feature_columns,
    "importance": xgb_model.feature_importances_
})

xgb_importance = xgb_importance.sort_values(
    "importance",
    ascending=False
).reset_index(drop=True)

print("\nXGBoost feature importance:")
print(
    xgb_importance.to_string(index=False)
)

xgb_importance.to_csv(
    f"{OUTPUT_DIR}/xgboost_feature_importance.csv",
    index=False
)


# ============================================================
# XGBOOST PLOT
# ============================================================

xgb_plot = xgb_importance.sort_values(
    "importance",
    ascending=True
)

plt.figure(figsize=(10, 8))

plt.barh(
    xgb_plot["feature"],
    xgb_plot["importance"]
)

plt.title(
    "XGBoost Feature Importance"
)

plt.xlabel(
    "Feature Importance"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/xgboost_feature_importance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE ANALYSIS COMPLETE")
print("=" * 70)

print("\nSaved:")

print(
    "outputs/explainability/"
    "random_forest_feature_importance.csv"
)

print(
    "outputs/explainability/"
    "random_forest_feature_importance.png"
)

print(
    "outputs/explainability/"
    "xgboost_feature_importance.csv"
)

print(
    "outputs/explainability/"
    "xgboost_feature_importance.png"
)