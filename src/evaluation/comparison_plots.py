import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

METRICS_DIR = "outputs/metrics"
GRAPH_DIR = "outputs/graphs"

os.makedirs(GRAPH_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

final_path = (
    f"{METRICS_DIR}/model_comparison_final.csv"
)

walk_path = (
    f"{METRICS_DIR}/model_comparison_walk_forward.csv"
)

final_df = pd.read_csv(final_path)
walk_df = pd.read_csv(walk_path)


# ============================================================
# 1. FINAL TEST — MAE
# ============================================================

plt.figure(figsize=(12, 7))

plt.bar(
    final_df["model"],
    final_df["MAE"]
)

plt.title(
    "Model Comparison — Final Test MAE"
)

plt.xlabel("Model")
plt.ylabel("MAE")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/model_comparison_final_mae.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 2. FINAL TEST — RMSE
# ============================================================

plt.figure(figsize=(12, 7))

plt.bar(
    final_df["model"],
    final_df["RMSE"]
)

plt.title(
    "Model Comparison — Final Test RMSE"
)

plt.xlabel("Model")
plt.ylabel("RMSE")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/model_comparison_final_rmse.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 3. FINAL TEST — MAPE
# ============================================================

plt.figure(figsize=(12, 7))

plt.bar(
    final_df["model"],
    final_df["MAPE"]
)

plt.title(
    "Model Comparison — Final Test MAPE"
)

plt.xlabel("Model")
plt.ylabel("MAPE (%)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/model_comparison_final_mape.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 4. WALK-FORWARD — MAE
# ============================================================

plt.figure(figsize=(12, 7))

plt.bar(
    walk_df["model"],
    walk_df["MAE"]
)

plt.title(
    "Model Comparison — Walk-Forward Average MAE"
)

plt.xlabel("Model")
plt.ylabel("MAE")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/model_comparison_walk_forward_mae.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 5. WALK-FORWARD — RMSE
# ============================================================

plt.figure(figsize=(12, 7))

plt.bar(
    walk_df["model"],
    walk_df["RMSE"]
)

plt.title(
    "Model Comparison — Walk-Forward Average RMSE"
)

plt.xlabel("Model")
plt.ylabel("RMSE")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/model_comparison_walk_forward_rmse.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 6. WALK-FORWARD — MAPE
# ============================================================

plt.figure(figsize=(12, 7))

plt.bar(
    walk_df["model"],
    walk_df["MAPE"]
)

plt.title(
    "Model Comparison — Walk-Forward Average MAPE"
)

plt.xlabel("Model")
plt.ylabel("MAPE (%)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/model_comparison_walk_forward_mape.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 7. FINAL TEST — ALL THREE METRICS
# ============================================================

fig, axes = plt.subplots(
    3,
    1,
    figsize=(13, 16)
)

axes[0].bar(
    final_df["model"],
    final_df["MAE"]
)

axes[0].set_title(
    "Final Test — MAE"
)

axes[0].set_ylabel("MAE")

axes[0].tick_params(
    axis="x",
    rotation=45
)


axes[1].bar(
    final_df["model"],
    final_df["RMSE"]
)

axes[1].set_title(
    "Final Test — RMSE"
)

axes[1].set_ylabel("RMSE")

axes[1].tick_params(
    axis="x",
    rotation=45
)


axes[2].bar(
    final_df["model"],
    final_df["MAPE"]
)

axes[2].set_title(
    "Final Test — MAPE"
)

axes[2].set_ylabel("MAPE (%)")

axes[2].tick_params(
    axis="x",
    rotation=45
)

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/model_comparison_final_all_metrics.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 8. ML-ONLY FINAL TEST
# ============================================================

ml_models = [
    "Random Forest",
    "XGBoost",
    "LSTM",
    "GRU"
]

ml_final = final_df[
    final_df["model"].isin(ml_models)
].copy()

fig, axes = plt.subplots(
    3,
    1,
    figsize=(11, 14)
)

axes[0].bar(
    ml_final["model"],
    ml_final["MAE"]
)

axes[0].set_title(
    "Machine Learning Models — Final Test MAE"
)

axes[0].set_ylabel("MAE")


axes[1].bar(
    ml_final["model"],
    ml_final["RMSE"]
)

axes[1].set_title(
    "Machine Learning Models — Final Test RMSE"
)

axes[1].set_ylabel("RMSE")


axes[2].bar(
    ml_final["model"],
    ml_final["MAPE"]
)

axes[2].set_title(
    "Machine Learning Models — Final Test MAPE"
)

axes[2].set_ylabel("MAPE (%)")

plt.tight_layout()

plt.savefig(
    f"{GRAPH_DIR}/ml_models_final_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print("=" * 70)
print("MODEL COMPARISON GRAPHS CREATED")
print("=" * 70)

print("\nSaved graphs:")

print(
    "outputs/graphs/model_comparison_final_mae.png"
)

print(
    "outputs/graphs/model_comparison_final_rmse.png"
)

print(
    "outputs/graphs/model_comparison_final_mape.png"
)

print(
    "outputs/graphs/model_comparison_walk_forward_mae.png"
)

print(
    "outputs/graphs/model_comparison_walk_forward_rmse.png"
)

print(
    "outputs/graphs/model_comparison_walk_forward_mape.png"
)

print(
    "outputs/graphs/model_comparison_final_all_metrics.png"
)

print(
    "outputs/graphs/ml_models_final_comparison.png"
)