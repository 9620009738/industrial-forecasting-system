import os
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/processed/iip_food_products_baseline_2012_2025.csv"

SEQ_LEN = 12
FORECAST_HORIZON = 12

EPOCHS = 150
BATCH_SIZE = 8

VALIDATION_YEARS = [2021, 2022, 2023]

FINAL_TEST_START = "2024-04-01"
FINAL_TEST_END = "2025-03-01"

np.random.seed(42)
tf.random.set_seed(42)


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(actual, predicted):

    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    mape = np.mean(
        np.abs((actual - predicted) / actual)
    ) * 100

    return mae, rmse, mape


# ============================================================
# CREATE SEQUENCES
# ============================================================

def create_sequences(values, seq_len):

    X = []
    y = []

    for i in range(seq_len, len(values)):

        X.append(values[i - seq_len:i])

        y.append(values[i])

    return np.array(X), np.array(y)


# ============================================================
# BUILD GRU MODEL
# ============================================================

def build_model():

    model = Sequential([
        Input(shape=(SEQ_LEN, 1)),

        GRU(
            64,
            return_sequences=True
        ),

        Dropout(0.2),

        GRU(32),

        Dropout(0.2),

        Dense(16, activation="relu"),

        Dense(1)
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.001
        ),
        loss="mse",
        metrics=["mae"]
    )

    return model


# ============================================================
# TRAIN + FORECAST
# ============================================================

def train_and_forecast(
    train_series,
    forecast_horizon=12
):

    train_values = train_series.values.reshape(-1, 1)

    scaler = MinMaxScaler()

    # Fit scaler ONLY on training data
    scaled_values = scaler.fit_transform(
        train_values
    )

    X, y = create_sequences(
        scaled_values,
        SEQ_LEN
    )

    X = X.reshape(
        X.shape[0],
        X.shape[1],
        1
    )

    y = y.reshape(-1, 1)

    model = build_model()

    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=20,
        restore_best_weights=True
    )

    model.fit(
        X,
        y,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.15,
        shuffle=False,
        callbacks=[early_stopping],
        verbose=0
    )

    # --------------------------------------------------------
    # Recursive 12-month forecasting
    # --------------------------------------------------------

    history_values = scaled_values.flatten().tolist()

    predictions_scaled = []

    for _ in range(forecast_horizon):

        sequence = np.array(
            history_values[-SEQ_LEN:]
        ).reshape(
            1,
            SEQ_LEN,
            1
        )

        prediction = model.predict(
            sequence,
            verbose=0
        )[0, 0]

        predictions_scaled.append(
            prediction
        )

        history_values.append(
            prediction
        )

    predictions = scaler.inverse_transform(
        np.array(predictions_scaled).reshape(-1, 1)
    ).flatten()

    return predictions, model


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("GRU INDUSTRIAL PRODUCTION FORECASTING")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)

df = df[
    ["date", "index"]
].rename(
    columns={"index": "target"}
)

print("\nFull dataset:")
print(
    df["date"].min(),
    "to",
    df["date"].max()
)

print(
    "Rows:",
    len(df)
)


# ============================================================
# MATCH ML EVALUATION START
# ============================================================

# RF, XGBoost and corrected LSTM all begin
# ML evaluation from April 2013.

ml_df = df[
    df["date"] >= "2013-04-01"
].copy()

ml_df = ml_df.reset_index(drop=True)

print("\nML evaluation dataset:")
print(
    ml_df["date"].min(),
    "to",
    ml_df["date"].max()
)

print(
    "Rows:",
    len(ml_df)
)


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

os.makedirs(
    "outputs/forecasts",
    exist_ok=True
)

os.makedirs(
    "outputs/metrics",
    exist_ok=True
)

os.makedirs(
    "models",
    exist_ok=True
)


# ============================================================
# WALK-FORWARD VALIDATION
# ============================================================

walk_forward_results = []


for validation_year in VALIDATION_YEARS:

    validation_start = pd.Timestamp(
        f"{validation_year}-01-01"
    )

    validation_end = pd.Timestamp(
        f"{validation_year}-12-01"
    )

    train_df = ml_df[
        ml_df["date"] < validation_start
    ].copy()

    validation_df = ml_df[
        (ml_df["date"] >= validation_start)
        &
        (ml_df["date"] <= validation_end)
    ].copy()

    train_series = train_df["target"]

    actual = validation_df["target"].values

    print("\n" + "=" * 70)

    print(
        f"Validation Year: {validation_year}"
    )

    print("=" * 70)

    print(
        "Training period:",
        train_df["date"].min().strftime("%Y-%m"),
        "to",
        train_df["date"].max().strftime("%Y-%m")
    )

    print(
        "Training rows:",
        len(train_df)
    )

    print(
        "Validation period:",
        validation_df["date"].min().strftime("%Y-%m"),
        "to",
        validation_df["date"].max().strftime("%Y-%m")
    )

    predicted, model = train_and_forecast(
        train_series,
        FORECAST_HORIZON
    )

    mae, rmse, mape = calculate_metrics(
        actual,
        predicted
    )

    print(
        f"MAE  : {mae:.6f}"
    )

    print(
        f"RMSE : {rmse:.6f}"
    )

    print(
        f"MAPE : {mape:.6f}%"
    )

    walk_forward_results.append({
        "validation_year": validation_year,
        "mae": mae,
        "rmse": rmse,
        "mape": mape
    })

    forecast_df = pd.DataFrame({
        "date": validation_df["date"].values,
        "actual": actual,
        "forecast": predicted
    })

    forecast_df.to_csv(
        f"outputs/forecasts/"
        f"gru_validation_{validation_year}.csv",
        index=False
    )


# ============================================================
# WALK-FORWARD SUMMARY
# ============================================================

walk_df = pd.DataFrame(
    walk_forward_results
)

print("\n" + "=" * 70)
print("GRU WALK-FORWARD SUMMARY")
print("=" * 70)

print(walk_df)

print("\nAverage validation metrics:")

print(
    f"MAE  : {walk_df['mae'].mean():.6f}"
)

print(
    f"RMSE : {walk_df['rmse'].mean():.6f}"
)

print(
    f"MAPE : {walk_df['mape'].mean():.6f}%"
)

walk_df.to_csv(
    "outputs/metrics/gru_walk_forward_metrics.csv",
    index=False
)


# ============================================================
# FINAL TEST
# ============================================================

final_train_df = ml_df[
    ml_df["date"] < FINAL_TEST_START
].copy()

final_test_df = ml_df[
    (ml_df["date"] >= FINAL_TEST_START)
    &
    (ml_df["date"] <= FINAL_TEST_END)
].copy()

print("\n" + "=" * 70)
print("GRU FINAL TEST")
print("=" * 70)

print(
    "Training:",
    final_train_df["date"].min().strftime("%Y-%m"),
    "to",
    final_train_df["date"].max().strftime("%Y-%m")
)

print(
    "Training rows:",
    len(final_train_df)
)

print(
    "Final test:",
    final_test_df["date"].min().strftime("%Y-%m"),
    "to",
    final_test_df["date"].max().strftime("%Y-%m")
)

print(
    "Test rows:",
    len(final_test_df)
)


final_predictions, final_model = train_and_forecast(
    final_train_df["target"],
    FORECAST_HORIZON
)

final_actual = final_test_df["target"].values

final_mae, final_rmse, final_mape = calculate_metrics(
    final_actual,
    final_predictions
)

print("\nFinal test metrics:")

print(
    f"MAE  : {final_mae:.6f}"
)

print(
    f"RMSE : {final_rmse:.6f}"
)

print(
    f"MAPE : {final_mape:.6f}%"
)


# ============================================================
# SAVE FINAL FORECAST
# ============================================================

final_forecast_df = pd.DataFrame({
    "date": final_test_df["date"].values,
    "actual": final_actual,
    "forecast": final_predictions
})

final_forecast_df.to_csv(
    "outputs/forecasts/gru_final_test.csv",
    index=False
)


# ============================================================
# SAVE FINAL MODEL
# ============================================================

final_model.save(
    "models/gru_food_products.keras"
)


# ============================================================
# SAVE FINAL METRICS
# ============================================================

final_metrics_df = pd.DataFrame([{
    "model": "GRU",
    "mae": final_mae,
    "rmse": final_rmse,
    "mape": final_mape
}])

final_metrics_df.to_csv(
    "outputs/metrics/gru_final_test_metrics.csv",
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("GRU COMPLETE")
print("=" * 70)

print("\nSaved:")

print(
    "outputs/forecasts/gru_final_test.csv"
)

print(
    "outputs/metrics/gru_final_test_metrics.csv"
)

print(
    "outputs/metrics/gru_walk_forward_metrics.csv"
)

print(
    "models/gru_food_products.keras"
)