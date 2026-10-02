from flask import Blueprint, request, jsonify
from pathlib import Path
import numpy as np
import pandas as pd

model_routes = Blueprint("model_routes", __name__)

UPLOAD_FOLDER = Path("data/uploads")
PROCESSED_FOLDER = Path("data/processed")

# ------------------------------------------------------------
# Common helpers
# ------------------------------------------------------------

def _dataset_path(dataset_id):
    if not dataset_id:
        raise ValueError("Dataset ID is required.")

    candidates = [
        UPLOAD_FOLDER / dataset_id,
        PROCESSED_FOLDER / dataset_id,
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError("Dataset not found.")


def _read_dataset(dataset_id):
    path = _dataset_path(dataset_id)

    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)

    return pd.read_csv(path)


def _prepare_series(dataset_id, date_column, target_column):
    df = _read_dataset(dataset_id)

    if date_column not in df.columns:
        raise ValueError(f"Date column '{date_column}' not found.")

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found.")

    df = df[[date_column, target_column]].copy()

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    df[target_column] = pd.to_numeric(
        df[target_column],
        errors="coerce"
    )

    df = (
        df.dropna(subset=[date_column, target_column])
        .sort_values(date_column)
        .drop_duplicates(subset=[date_column], keep="last")
        .reset_index(drop=True)
    )

    if len(df) < 36:
        raise ValueError(
            "At least 36 valid observations are required for the forecasting models."
        )

    return df


def _historical(df, date_column, target_column):
    return [
        {
            "date": date_value.strftime("%Y-%m-%d"),
            "value": float(value),
        }
        for date_value, value in zip(
            df[date_column],
            df[target_column]
        )
    ]


def _forecast_dates(last_date, horizon):
    # The current project is monthly. MS keeps the forecast aligned
    # to the first day of each month.
    return pd.date_range(
        start=last_date + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq="MS"
    )


def _response(model_info, historical, forecast, metrics=None):
    payload = {
        "success": True,
        "model": model_info,
        "historical": historical,
        "forecast": forecast,
    }

    if metrics:
        payload["metrics"] = metrics

    return jsonify(payload)


def _safe_horizon(value):
    try:
        horizon = int(value)
    except (TypeError, ValueError):
        horizon = 12

    return max(1, min(horizon, 60))


# ------------------------------------------------------------
# Machine-learning feature engineering
# ------------------------------------------------------------

ML_FEATURES = [
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


def _feature_row(history, forecast_date):
    values = pd.Series(
        history,
        dtype="float64"
    )

    if len(values) < 13:
        raise ValueError(
            "At least 13 historical observations are required for lag-12 features."
        )

    row = {
        "month_number": int(forecast_date.month),
        "quarter": int(forecast_date.quarter),
        "year_number": int(forecast_date.year),
        "month_sin": float(
            np.sin(2 * np.pi * forecast_date.month / 12)
        ),
        "month_cos": float(
            np.cos(2 * np.pi * forecast_date.month / 12)
        ),
        "lag_1": float(values.iloc[-1]),
        "lag_2": float(values.iloc[-2]),
        "lag_3": float(values.iloc[-3]),
        "lag_6": float(values.iloc[-6]),
        "lag_12": float(values.iloc[-12]),
        "rolling_mean_3": float(values.iloc[-3:].mean()),
        "rolling_std_3": float(
            values.iloc[-3:].std(ddof=0)
        ),
        "rolling_mean_6": float(values.iloc[-6:].mean()),
        "rolling_std_6": float(
            values.iloc[-6:].std(ddof=0)
        ),
        "rolling_mean_12": float(values.iloc[-12:].mean()),
        "rolling_std_12": float(
            values.iloc[-12:].std(ddof=0)
        ),
    }

    return pd.DataFrame(
        [row],
        columns=ML_FEATURES
    )


def _training_features(df, date_column, target_column):
    work = df[[date_column, target_column]].copy()

    work["month_number"] = work[date_column].dt.month
    work["quarter"] = work[date_column].dt.quarter
    work["year_number"] = work[date_column].dt.year
    work["month_sin"] = np.sin(
        2 * np.pi * work["month_number"] / 12
    )
    work["month_cos"] = np.cos(
        2 * np.pi * work["month_number"] / 12
    )

    for lag in [1, 2, 3, 6, 12]:
        work[f"lag_{lag}"] = work[target_column].shift(lag)

    shifted = work[target_column].shift(1)

    for window in [3, 6, 12]:
        work[f"rolling_mean_{window}"] = (
            shifted.rolling(window).mean()
        )
        work[f"rolling_std_{window}"] = (
            shifted.rolling(window).std(ddof=0)
        )

    work = work.dropna().reset_index(drop=True)

    if len(work) < 24:
        raise ValueError(
            "Not enough observations remain after creating lag and rolling features."
        )

    X = work[ML_FEATURES].astype(float)
    y = work[target_column].astype(float)

    return X, y


def _recursive_forecast(regressor, df, date_column, target_column, horizon):
    history = (
        df[target_column]
        .astype(float)
        .tolist()
    )

    dates = _forecast_dates(
        df[date_column].iloc[-1],
        horizon
    )

    forecasts = []

    for forecast_date in dates:
        features = _feature_row(
            history,
            forecast_date
        )

        prediction = float(
            regressor.predict(features)[0]
        )

        forecasts.append(
            {
                "date": forecast_date.strftime("%Y-%m-%d"),
                "value": prediction,
            }
        )

        history.append(prediction)

    return forecasts


# ------------------------------------------------------------
# SARIMAX
# ------------------------------------------------------------

@model_routes.route(
    "/api/models/sarimax",
    methods=["POST"]
)
def run_sarimax_model():
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        data = request.get_json() or {}

        dataset_id = data.get("dataset_id")
        date_column = data.get("date_column")
        target_column = data.get("target_column")
        requested_exog = data.get("exog_column")
        horizon = _safe_horizon(data.get("horizon", 12))

        df = _prepare_series(
            dataset_id,
            date_column,
            target_column
        )

        # First priority: explicitly selected numeric column in the
        # uploaded dataset.
        exog_name = None
        exog_series = None

        full_df = _read_dataset(dataset_id)

        if requested_exog:
            if requested_exog not in full_df.columns:
                raise ValueError(
                    f"External variable '{requested_exog}' not found."
                )

            candidate = pd.DataFrame({
                "date": pd.to_datetime(
                    full_df[date_column],
                    errors="coerce"
                ),
                "value": pd.to_numeric(
                    full_df[requested_exog],
                    errors="coerce"
                ),
            }).dropna()

            candidate = candidate.sort_values("date")

            merged = df.merge(
                candidate,
                left_on=date_column,
                right_on="date",
                how="inner"
            )

            if len(merged) < 36:
                raise ValueError(
                    "The selected external variable does not have enough overlapping observations."
                )

            df_model = merged[[date_column, target_column, "value"]].copy()
            df_model = df_model.rename(
                columns={"value": requested_exog}
            )
            exog_name = requested_exog
            exog_series = df_model[requested_exog].astype(float)

        else:
            # Project-specific CPI integration. This is the external
            # variable used in the research extension when available.
            cpi_path = Path(
                "data/raw/external/cpi_general_all_india_2013_2025.csv"
            )

            if cpi_path.exists():
                cpi = pd.read_csv(cpi_path)

                cpi_date_col = "date"
                cpi_value_col = "cpi_general_combined"

                if cpi_date_col in cpi.columns and cpi_value_col in cpi.columns:
                    cpi[cpi_date_col] = pd.to_datetime(
                        cpi[cpi_date_col],
                        errors="coerce"
                    )
                    cpi[cpi_value_col] = pd.to_numeric(
                        cpi[cpi_value_col],
                        errors="coerce"
                    )
                    cpi = cpi.dropna(
                        subset=[cpi_date_col, cpi_value_col]
                    )

                    merged = df.merge(
                        cpi[[cpi_date_col, cpi_value_col]],
                        left_on=date_column,
                        right_on=cpi_date_col,
                        how="inner"
                    )

                    if len(merged) >= 36:
                        df_model = merged[
                            [date_column, target_column, cpi_value_col]
                        ].copy()

                        exog_name = "CPI General"
                        exog_series = df_model[cpi_value_col].astype(float)

        if exog_series is None:
            raise ValueError(
                "SARIMAX requires an external variable. Select a numeric "
                "external column or place the project CPI file at "
                "data/raw/external/cpi_general_all_india_2013_2025.csv."
            )

        y = df_model[target_column].astype(float)

        model = SARIMAX(
            y,
            exog=exog_series.to_frame(),
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )

        fitted = model.fit(disp=False)

        # Future exogenous values must be supplied to SARIMAX.
        # For the project's CPI extension, forecast the external
        # series with Holt-Winters. For a user-uploaded external
        # column, repeat the last value as a transparent baseline.
        future_exog_values = []

        if exog_name == "CPI General":
            cpi_model = ExponentialSmoothing(
                exog_series.astype(float),
                trend="add",
                seasonal="add",
                seasonal_periods=12,
                initialization_method="estimated",
            ).fit(optimized=True)

            future_exog_values = [
                float(value)
                for value in cpi_model.forecast(horizon)
            ]
        else:
            future_exog_values = [
                float(exog_series.iloc[-1])
                for _ in range(horizon)
            ]

        future_exog = pd.DataFrame({
            exog_series.name: future_exog_values
        })

        forecast_result = fitted.get_forecast(
            steps=horizon,
            exog=future_exog
        )

        point = forecast_result.predicted_mean
        interval = forecast_result.conf_int()

        dates = _forecast_dates(
            df_model[date_column].iloc[-1],
            horizon
        )

        forecast = []

        for index, date_value in enumerate(dates):
            forecast.append({
                "date": date_value.strftime("%Y-%m-%d"),
                "value": float(point.iloc[index]),
                "lower": float(interval.iloc[index, 0]),
                "upper": float(interval.iloc[index, 1]),
            })

        parameters = {
            "order": "(1,1,1)",
            "seasonal_order": "(1,1,1,12)",
            "external_variable": exog_name,
            "external_forecast": (
                "Holt-Winters"
                if exog_name == "CPI General"
                else "Last observed value baseline"
            ),
            "seasonal_period": 12,
            "horizon": horizon,
        }

        model_info = {
            "name": "SARIMAX",
            "type": "Statistical Forecasting with Exogenous Variable",
            "observations": int(len(y)),
            "horizon": horizon,
            "aic": float(fitted.aic),
            "bic": float(fitted.bic),
            "parameters": parameters,
        }

        return _response(
            model_info,
            _historical(
                df_model,
                date_column,
                target_column
            ),
            forecast,
        )

    except Exception as error:
        print("SARIMAX error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ------------------------------------------------------------
# Random Forest
# ------------------------------------------------------------

@model_routes.route(
    "/api/models/random_forest",
    methods=["POST"]
)
def run_random_forest_model():
    try:
        from sklearn.ensemble import RandomForestRegressor

        data = request.get_json() or {}

        df = _prepare_series(
            data.get("dataset_id"),
            data.get("date_column"),
            data.get("target_column")
        )

        horizon = _safe_horizon(
            data.get("horizon", 12)
        )

        X, y = _training_features(
            df,
            data.get("date_column"),
            data.get("target_column")
        )

        model = RandomForestRegressor(
            n_estimators=500,
            max_features=1.0,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X, y)

        forecast = _recursive_forecast(
            model,
            df,
            data.get("date_column"),
            data.get("target_column"),
            horizon,
        )

        importance = dict(
            sorted(
                zip(
                    ML_FEATURES,
                    model.feature_importances_
                ),
                key=lambda item: item[1],
                reverse=True
            )[:10]
        )

        parameters = {
            "n_estimators": 500,
            "max_features": "1.0",
            "min_samples_leaf": 1,
            "random_state": 42,
            "feature_count": len(ML_FEATURES),
            "top_feature": max(
                importance,
                key=importance.get
            ),
        }

        model_info = {
            "name": "Random Forest",
            "type": "Machine Learning",
            "observations": int(len(df)),
            "horizon": horizon,
            "parameters": parameters,
        }

        return _response(
            model_info,
            _historical(
                df,
                data.get("date_column"),
                data.get("target_column")
            ),
            forecast,
        )

    except Exception as error:
        print("Random Forest error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ------------------------------------------------------------
# XGBoost
# ------------------------------------------------------------

@model_routes.route(
    "/api/models/xgboost",
    methods=["POST"]
)
def run_xgboost_model():
    try:
        from xgboost import XGBRegressor

        data = request.get_json() or {}

        df = _prepare_series(
            data.get("dataset_id"),
            data.get("date_column"),
            data.get("target_column")
        )

        horizon = _safe_horizon(
            data.get("horizon", 12)
        )

        X, y = _training_features(
            df,
            data.get("date_column"),
            data.get("target_column")
        )

        model = XGBRegressor(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=4,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X, y)

        forecast = _recursive_forecast(
            model,
            df,
            data.get("date_column"),
            data.get("target_column"),
            horizon,
        )

        importance = dict(
            sorted(
                zip(
                    ML_FEATURES,
                    model.feature_importances_
                ),
                key=lambda item: item[1],
                reverse=True
            )[:10]
        )

        parameters = {
            "n_estimators": 500,
            "learning_rate": 0.03,
            "max_depth": 4,
            "min_child_weight": 2,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "feature_count": len(ML_FEATURES),
            "top_feature": max(
                importance,
                key=importance.get
            ),
        }

        model_info = {
            "name": "XGBoost",
            "type": "Machine Learning",
            "observations": int(len(df)),
            "horizon": horizon,
            "parameters": parameters,
        }

        return _response(
            model_info,
            _historical(
                df,
                data.get("date_column"),
                data.get("target_column")
            ),
            forecast,
        )

    except Exception as error:
        print("XGBoost error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ------------------------------------------------------------
# LSTM / GRU
# ------------------------------------------------------------

def _run_recurrent_model(
    model_name,
    dataset_id,
    date_column,
    target_column,
    horizon,
):
    from sklearn.preprocessing import MinMaxScaler
    import tensorflow as tf

    df = _prepare_series(
        dataset_id,
        date_column,
        target_column
    )

    values = (
        df[target_column]
        .astype(float)
        .values
        .reshape(-1, 1)
    )

    sequence_length = 12

    if len(values) <= sequence_length + 12:
        raise ValueError(
            "At least 25 observations are required for recurrent forecasting."
        )

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X = []
    y = []

    for index in range(
        sequence_length,
        len(scaled)
    ):
        X.append(
            scaled[
                index - sequence_length:index,
                0
            ]
        )
        y.append(
            scaled[index, 0]
        )

    X = np.array(X).reshape(
        -1,
        sequence_length,
        1
    )

    y = np.array(y)

    tf.keras.backend.clear_session()

    model = tf.keras.Sequential()

    if model_name == "LSTM":
        model.add(
            tf.keras.layers.LSTM(
                64,
                return_sequences=True,
                input_shape=(
                    sequence_length,
                    1
                ),
            )
        )
        model.add(
            tf.keras.layers.Dropout(0.2)
        )
        model.add(
            tf.keras.layers.LSTM(32)
        )
    else:
        model.add(
            tf.keras.layers.GRU(
                64,
                return_sequences=True,
                input_shape=(
                    sequence_length,
                    1
                ),
            )
        )
        model.add(
            tf.keras.layers.Dropout(0.2)
        )
        model.add(
            tf.keras.layers.GRU(32)
        )

    model.add(
        tf.keras.layers.Dropout(0.2)
    )
    model.add(
        tf.keras.layers.Dense(16, activation="relu")
    )
    model.add(
        tf.keras.layers.Dense(1)
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.001
        ),
        loss="mse",
        metrics=["mae"],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=20,
            restore_best_weights=True,
        )
    ]

    model.fit(
        X,
        y,
        epochs=150,
        batch_size=8,
        validation_split=0.15,
        shuffle=False,
        callbacks=callbacks,
        verbose=0,
    )

    history = (
        scaled[-sequence_length:, 0]
        .tolist()
    )

    future_dates = _forecast_dates(
        df[date_column].iloc[-1],
        horizon
    )

    forecast = []

    for date_value in future_dates:
        sequence = np.array(
            history[-sequence_length:],
            dtype=float
        ).reshape(
            1,
            sequence_length,
            1
        )

        predicted_scaled = float(
            model.predict(
                sequence,
                verbose=0
            )[0, 0]
        )

        predicted_value = float(
            scaler.inverse_transform(
                np.array(
                    [[predicted_scaled]]
                )
            )[0, 0]
        )

        forecast.append({
            "date": date_value.strftime("%Y-%m-%d"),
            "value": predicted_value,
        })

        history.append(predicted_scaled)

    parameters = {
        "sequence_length": sequence_length,
        "first_recurrent_units": 64,
        "second_recurrent_units": 32,
        "dropout": 0.2,
        "dense_units": 16,
        "optimizer": "Adam",
        "learning_rate": 0.001,
        "epochs_max": 150,
        "batch_size": 8,
        "validation_split": 0.15,
        "early_stopping_patience": 20,
    }

    model_info = {
        "name": model_name,
        "type": "Deep Learning",
        "observations": int(len(df)),
        "horizon": horizon,
        "parameters": parameters,
    }

    return (
        model_info,
        _historical(
            df,
            date_column,
            target_column
        ),
        forecast,
    )


@model_routes.route(
    "/api/models/lstm",
    methods=["POST"]
)
def run_lstm_model():
    try:
        data = request.get_json() or {}

        model_info, historical, forecast = _run_recurrent_model(
            "LSTM",
            data.get("dataset_id"),
            data.get("date_column"),
            data.get("target_column"),
            _safe_horizon(data.get("horizon", 12)),
        )

        return _response(
            model_info,
            historical,
            forecast,
        )

    except Exception as error:
        print("LSTM error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@model_routes.route(
    "/api/models/gru",
    methods=["POST"]
)
def run_gru_model():
    try:
        data = request.get_json() or {}

        model_info, historical, forecast = _run_recurrent_model(
            "GRU",
            data.get("dataset_id"),
            data.get("date_column"),
            data.get("target_column"),
            _safe_horizon(data.get("horizon", 12)),
        )

        return _response(
            model_info,
            historical,
            forecast,
        )

    except Exception as error:
        print("GRU error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500
