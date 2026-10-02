from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "iip_food_products_baseline_2012_2025.csv"
)

TARGET = "index"

SEQUENCE_LENGTH = 12


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
# CREATE SEQUENCES
# ============================================================

def create_sequences(values, sequence_length=12):

    X = []
    y = []

    for i in range(
        sequence_length,
        len(values)
    ):

        X.append(
            values[
                i - sequence_length:i
            ]
        )

        y.append(
            values[i]
        )

    X = np.array(X)
    y = np.array(y)

    # LSTM/GRU expects:
    # samples × timesteps × features

    X = X.reshape(
        X.shape[0],
        X.shape[1],
        1,
    )

    return X, y


# ============================================================
# PREPARE TRAINING DATA
# ============================================================

def prepare_training_data(
    training_df,
    sequence_length=12,
):

    values = (
        training_df[TARGET]
        .to_numpy()
        .reshape(-1, 1)
    )

    scaler = MinMaxScaler()

    scaled_values = scaler.fit_transform(
        values
    )

    X, y = create_sequences(
        scaled_values,
        sequence_length,
    )

    return X, y, scaler


# ============================================================
# PREPARE VALIDATION INPUT
# ============================================================

def prepare_validation_history(
    training_df,
    scaler,
    sequence_length=12,
):

    values = (
        training_df[TARGET]
        .to_numpy()
        .reshape(-1, 1)
    )

    scaled_values = scaler.transform(
        values
    )

    if len(scaled_values) < sequence_length:

        raise ValueError(
            "Not enough historical observations "
            "to create an LSTM sequence."
        )

    return scaled_values[
        -sequence_length:
    ].reshape(
        1,
        sequence_length,
        1,
    )


# ============================================================
# RECURSIVE FUTURE INPUT
# ============================================================

def create_next_sequence(
    history_scaled,
    prediction_scaled,
    sequence_length=12,
):

    updated_history = np.concatenate(
        [
            history_scaled,
            np.array(
                [[prediction_scaled]]
            ),
        ],
        axis=0,
    )

    next_sequence = (
        updated_history[
            -sequence_length:
        ]
        .reshape(
            1,
            sequence_length,
            1,
        )
    )

    return (
        updated_history,
        next_sequence,
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_sequence_pipeline():

    print("=" * 70)
    print(
        "LSTM / GRU SEQUENCE PIPELINE VALIDATION"
    )
    print("=" * 70)

    df = load_data()

    print("\nDataset:")
    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Date range: "
        f"{df['date'].min()} → "
        f"{df['date'].max()}"
    )

    # --------------------------------------------------------
    # DEVELOPMENT DATA
    # --------------------------------------------------------

    development_df = df[
        df["date"]
        < pd.Timestamp("2024-04-01")
    ].copy()

    final_test_df = df[
        df["date"]
        >= pd.Timestamp("2024-04-01")
    ].copy()

    print("\nDevelopment dataset:")
    print(
        f"Rows: {len(development_df)}"
    )

    print(
        f"Range: "
        f"{development_df['date'].min()} → "
        f"{development_df['date'].max()}"
    )

    print("\nFinal test dataset:")
    print(
        f"Rows: {len(final_test_df)}"
    )

    print(
        f"Range: "
        f"{final_test_df['date'].min()} → "
        f"{final_test_df['date'].max()}"
    )

    # --------------------------------------------------------
    # SCALER
    # --------------------------------------------------------

    X_train, y_train, scaler = (
        prepare_training_data(
            development_df,
            SEQUENCE_LENGTH,
        )
    )

    print("\nSequence generation:")
    print(
        f"Sequence length: "
        f"{SEQUENCE_LENGTH}"
    )

    print(
        f"X shape: "
        f"{X_train.shape}"
    )

    print(
        f"y shape: "
        f"{y_train.shape}"
    )

    # --------------------------------------------------------
    # EXPECTED SHAPE
    # --------------------------------------------------------

    expected_rows = (
        len(development_df)
        - SEQUENCE_LENGTH
    )

    if X_train.shape[0] != expected_rows:

        raise ValueError(
            "Unexpected number of training sequences."
        )

    if X_train.shape[1] != SEQUENCE_LENGTH:

        raise ValueError(
            "Unexpected sequence length."
        )

    if X_train.shape[2] != 1:

        raise ValueError(
            "Unexpected number of features."
        )

    print(
        "Training sequence shape: PASS"
    )

    # --------------------------------------------------------
    # SCALER LEAKAGE CHECK
    # --------------------------------------------------------

    development_min = (
        development_df[TARGET].min()
    )

    development_max = (
        development_df[TARGET].max()
    )

    scaler_min = (
        scaler.data_min_[0]
    )

    scaler_max = (
        scaler.data_max_[0]
    )

    if (
        scaler_min == development_min
        and scaler_max == development_max
    ):

        print(
            "Scaler fitted only on development data: PASS"
        )

    else:

        print(
            "Scaler development-only check: FAIL"
        )

    # --------------------------------------------------------
    # TEST DATA IS NOT USED IN SCALING
    # --------------------------------------------------------

    test_min = (
        final_test_df[TARGET].min()
    )

    test_max = (
        final_test_df[TARGET].max()
    )

    print(
        f"\nDevelopment target range: "
        f"{development_min:.4f} → "
        f"{development_max:.4f}"
    )

    print(
        f"Final test target range: "
        f"{test_min:.4f} → "
        f"{test_max:.4f}"
    )

    # --------------------------------------------------------
    # SAMPLE SEQUENCE
    # --------------------------------------------------------

    print("\nFirst training sequence:")

    print(
        X_train[0]
        .reshape(-1)
    )

    print(
        "\nFirst sequence target:"
    )

    print(
        y_train[0]
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print(
        "SEQUENCE PIPELINE VALIDATION PASSED"
    )
    print("=" * 70)


if __name__ == "__main__":
    validate_sequence_pipeline()