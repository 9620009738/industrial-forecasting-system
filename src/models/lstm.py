import os
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
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
# BUILD LSTM MODEL
# ============================================================

def build_model():

    model = Sequential([
        Input(shape=(SEQ_LEN, 1)),

        LSTM(
            64,
            return_sequences=True
        ),

        Dropout(0.2),

        LSTM(32),

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

    history = model.fit(
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
    # Recursive forecasting
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

    return predictions, model, history


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LSTM INDUSTRIAL PRODUCTION FORECASTING")
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

print("Rows:", len(df))


# ============================================================
# MATCH ML EVALUATION START
# ============================================================

# RF and XGBoost ML evaluation start from April 2013.
# Therefore LSTM uses the same starting point for
# directly comparable ML walk-forward evaluation.

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

print("Rows:", len(ml_df))


# ============================================================
# WALK-FORWARD VALIDATION
# ============================================================

walk_forward_results = []

os.makedirs(
    "outputs/forecasts",
    exist_ok=True
)

os.makedirs(
    "outputs/models",
    exist_ok=True
)

os.makedirs(
    "models",
    exist_ok=True
)

os.makedirs(
    "outputs/metrics",
    exist_ok=True
)

os.makedirs(
    "outputs/graphs",
    exist_ok=True
)


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

    predicted, model, history = train_and_forecast(
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

    forecast_path = (
        f"outputs/forecasts/"
        f"lstm_validation_{validation_year}.csv"
    )

    forecast_df.to_csv(
        forecast_path,
        index=False
    )


# ============================================================
# WALK-FORWARD SUMMARY
# ============================================================

walk_df = pd.DataFrame(
    walk_forward_results
)

print("\n" + "=" * 70)
print("LSTM WALK-FORWARD SUMMARY")
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
    "outputs/metrics/lstm_walk_forward_metrics.csv",
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
print("LSTM FINAL TEST")
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

final_predictions, final_model, final_history = train_and_forecast(
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
    "outputs/forecasts/lstm_final_test.csv",
    index=False
)


# ============================================================
# SAVE FINAL MODEL
# ============================================================

final_model.save(
    "models/lstm_food_products.keras"
)


# ============================================================
# SAVE FINAL METRICS
# ============================================================

final_metrics_df = pd.DataFrame([{
    "model": "LSTM",
    "mae": final_mae,
    "rmse": final_rmse,
    "mape": final_mape
}])

final_metrics_df.to_csv(
    "outputs/metrics/lstm_final_test_metrics.csv",
    index=False
)


# ============================================================
# SAVE TRAINING HISTORY
# ============================================================

history_df = pd.DataFrame(
    final_history.history
)

history_df.to_csv(
    "outputs/metrics/lstm_training_history.csv",
    index=False
)


print("\n" + "=" * 70)
print("LSTM COMPLETE")
print("=" * 70)

print(
    "\nSaved:"
)

print(
    "outputs/forecasts/lstm_final_test.csv"
)

print(
    "outputs/metrics/lstm_final_test_metrics.csv"
)

print(
    "outputs/metrics/lstm_walk_forward_metrics.csv"
)

print(
    "outputs/metrics/lstm_training_history.csv"
)

print(
    "models/lstm_food_products.keras"
)