from __future__ import annotations
import json
import math
import os
import re
import uuid
import warnings
import secrets
import importlib
import smtplib
from email.message import EmailMessage
from functools import wraps
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_file, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

warnings.filterwarnings("ignore", category=FutureWarning)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "data" / "uploads"
PROCESSED_FOLDER = BASE_DIR / "data" / "processed"
EXTERNAL_FOLDER = BASE_DIR / "data" / "raw" / "external"
OUTPUT_FOLDER = BASE_DIR / "outputs"
EXPLAIN_FOLDER = OUTPUT_FOLDER / "explainability"
REPORT_FOLDER = OUTPUT_FOLDER / "reports"
DATABASE_FOLDER = BASE_DIR / "data"
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
MONGO_DB_NAME = os.environ.get("MONGODB_DATABASE", "forecastiq")

for folder in [
    UPLOAD_FOLDER,
    PROCESSED_FOLDER,
    EXTERNAL_FOLDER,
    OUTPUT_FOLDER,
    EXPLAIN_FOLDER,
    REPORT_FOLDER,
]:
    folder.mkdir(parents=True, exist_ok=True)

DATABASE_FOLDER.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
app.config["SECRET_KEY"] = os.environ.get(
    "FORECASTIQ_SECRET_KEY",
    "change-this-development-secret-key",
)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        }
    },
    supports_credentials=True,
)


# ============================================================
# AUTHENTICATION / MONGODB DATABASE
# ============================================================

mongo_client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
)
db = mongo_client[MONGO_DB_NAME]
users_collection = db["users"]
datasets_collection = db["datasets"]
activity_logs_collection = db["activity_logs"]
report_history_collection = db["report_history"]
model_runs_collection = db["model_runs"]


def initialize_database():
    """Initialize ForecastIQ's MongoDB collections and indexes.

    Sprint 11 establishes the MongoDB foundation. Registration,
    authentication authorization, dataset ownership, audit logging,
    and admin management are implemented in subsequent sprints.
    """
    # Verify that the local/remote MongoDB server is reachable.
    mongo_client.admin.command("ping")

    # Indexes provide uniqueness and efficient administrative queries.
    users_collection.create_index("email", unique=True)
    users_collection.create_index([("role", ASCENDING), ("is_active", ASCENDING)])
    users_collection.create_index("created_at")

    datasets_collection.create_index("dataset_id", unique=True)
    datasets_collection.create_index("user_id")
    datasets_collection.create_index("uploaded_at")

    activity_logs_collection.create_index("user_id")
    activity_logs_collection.create_index("created_at")
    activity_logs_collection.create_index("action")

    report_history_collection.create_index("report_id", unique=True)
    report_history_collection.create_index("user_id")
    report_history_collection.create_index("created_at")

    model_runs_collection.create_index("user_id")
    model_runs_collection.create_index("created_at")

    admin_email = os.environ.get(
        "FORECASTIQ_ADMIN_EMAIL",
        "admin@forecastiq.local",
    ).strip().lower()
    admin_password = os.environ.get("FORECASTIQ_ADMIN_PASSWORD")

    existing = users_collection.find_one({"email": admin_email})

    # Only generate/print a password when an admin account actually needs
    # to be created. Never silently replace an existing admin password.
    if existing is None:
        if not admin_password:
            admin_password = secrets.token_urlsafe(16)
            print("Initial ForecastIQ admin password:", admin_password)

        now = datetime.now().isoformat()
        users_collection.insert_one(
            {
                "name": "ForecastIQ Administrator",
                "email": admin_email,
                "password_hash": generate_password_hash(admin_password),
                "role": "admin",
                "is_active": True,
                "created_at": now,
                "last_login_at": None,
            }
        )
    else:
        users_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {"role": "admin", "is_active": True}},
        )


initialize_database()


def serialize_object_id(value):
    return str(value) if isinstance(value, ObjectId) else value


def serialize_user(user):
    if not user:
        return None
    return {
        "id": serialize_object_id(user.get("_id")),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "user"),
        "is_active": bool(user.get("is_active", True)),
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
    }


def get_current_user_record():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        session.clear()
        return None
    user = users_collection.find_one({"_id": user_object_id})
    if user is None or not user.get("is_active", False):
        session.clear()
        return None
    return user


def require_auth(view_function):
    """Require an active authenticated ForecastIQ session."""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        user = get_current_user_record()

        if user is None:
            return error_response("Authentication required.", 401)

        return view_function(*args, **kwargs)

    return wrapped_view


def require_admin(view_function):
    """Require an active authenticated ForecastIQ administrator session."""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        user = get_current_user_record()

        if user is None:
            return error_response("Authentication required.", 401)

        if user.get("role") != "admin":
            return error_response("Administrator access required.", 403)

        return view_function(*args, **kwargs)

    return wrapped_view


def log_activity(user_id, action, resource_type=None, resource_id=None, details=None):
    """Write an auditable application event without storing passwords."""
    activity_logs_collection.insert_one(
        {
            "user_id": ObjectId(user_id) if user_id else None,
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "ip_address": request.headers.get("X-Forwarded-For", request.remote_addr),
            "user_agent": request.headers.get("User-Agent"),
            "details": details or {},
            "created_at": datetime.now().isoformat(),
        }
    )


# ============================================================
# PASSWORD RESET HELPERS
# ============================================================

PASSWORD_RESET_TTL_MINUTES = int(
    os.environ.get("FORECASTIQ_PASSWORD_RESET_TTL_MINUTES", "15")
)
PASSWORD_RESET_DEV_MODE = os.environ.get(
    "FORECASTIQ_PASSWORD_RESET_DEV_MODE",
    "true",
).strip().lower() in {"1", "true", "yes", "on"}


def send_password_reset_email(recipient, code):
    """Send a password-reset code when SMTP is configured.

    Local development can use PASSWORD_RESET_DEV_MODE and receive the
    one-time code directly in the API response. Production should disable
    that mode and configure SMTP.
    """
    smtp_host = os.environ.get("FORECASTIQ_SMTP_HOST")
    smtp_port = int(os.environ.get("FORECASTIQ_SMTP_PORT", "587"))
    smtp_username = os.environ.get("FORECASTIQ_SMTP_USERNAME")
    smtp_password = os.environ.get("FORECASTIQ_SMTP_PASSWORD")
    sender = os.environ.get(
        "FORECASTIQ_SMTP_FROM",
        smtp_username or "no-reply@forecastiq.local",
    )

    if not smtp_host:
        return False

    message = EmailMessage()
    message["Subject"] = "ForecastIQ password reset code"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "Your ForecastIQ password reset code is: "
        f"{code}\n\n"
        f"This code expires in {PASSWORD_RESET_TTL_MINUTES} minutes.\n"
        "If you did not request a password reset, ignore this email."
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.starttls()
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        server.send_message(message)

    return True


# ============================================================
# GENERAL HELPERS
# ============================================================

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def json_safe(value):
    """
    Recursively convert pandas / NumPy values into
    JSON-serializable Python values.

    Important:
    Containers such as dict/list must be handled BEFORE
    pd.isna(), because pd.isna() on an array/list can return
    multiple Boolean values and cause:

    ValueError:
    The truth value of an array with more than one element
    is ambiguous.
    """

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------
    if isinstance(value, dict):
        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    # --------------------------------------------------------
    # List / Tuple
    # --------------------------------------------------------
    if isinstance(value, (list, tuple)):
        return [
            json_safe(item)
            for item in value
        ]

    # --------------------------------------------------------
    # NumPy integer
    # --------------------------------------------------------
    if isinstance(value, np.integer):
        return int(value)

    # --------------------------------------------------------
    # NumPy floating point
    # --------------------------------------------------------
    if isinstance(value, np.floating):
        if np.isnan(value):
            return None

        return float(value)

    # --------------------------------------------------------
    # NumPy boolean
    # --------------------------------------------------------
    if isinstance(value, np.bool_):
        return bool(value)

    # --------------------------------------------------------
    # NumPy array
    # --------------------------------------------------------
    if isinstance(value, np.ndarray):
        return [
            json_safe(item)
            for item in value.tolist()
        ]

    # --------------------------------------------------------
    # Pandas / Python datetime
    # --------------------------------------------------------
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()

    # --------------------------------------------------------
    # Pandas NA / NaN / NaT
    # --------------------------------------------------------
    try:
        missing = pd.isna(value)

        if isinstance(missing, (bool, np.bool_)):
            if bool(missing):
                return None

    except (TypeError, ValueError):
        pass

    # --------------------------------------------------------
    # Normal Python value
    # --------------------------------------------------------
    return value


def error_response(message, status=400):
    return jsonify({"success": False, "error": str(message)}), status


def clean_name(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value))


def resolve_dataset(dataset_id: str | None):
    """Resolve an uploaded or processed dataset safely."""
    if not dataset_id:
        return None

    dataset_id = str(dataset_id)

    candidates = []

    for root in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
        exact = root / f"{dataset_id}.csv"
        if exact.exists():
            candidates.append(exact)

        # Uploaded files are commonly uuid.csv / uuid.xlsx.
        for path in root.glob(f"{dataset_id}.*"):
            candidates.append(path)

        # Clean endpoint may return the source id in a generated filename.
        for path in root.glob(f"*{dataset_id}*.csv"):
            candidates.append(path)

    # Prefer exact matches.
    for path in candidates:
        if path.exists() and path.is_file():
            return path

    return None


def read_dataset(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)

    raise ValueError(f"Unsupported dataset format: {suffix}")


def detect_date_columns(df: pd.DataFrame):
    result = []

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            continue

        parsed = pd.to_datetime(
            df[column],
            errors="coerce",
            format="mixed",
        )

        if parsed.notna().mean() >= 0.70:
            result.append(str(column))

    return result


def profile_dataset(df: pd.DataFrame):
    date_columns = detect_date_columns(df)
    numeric_columns = [
        str(c)
        for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    missing_columns = {}
    column_profiles = []

    for column in df.columns:
        series = df[column]
        missing = int(series.isna().sum())

        missing_columns[str(column)] = missing

        item = {
            "name": str(column),
            "dtype": str(series.dtype),
            "missing": missing,
            "missing_percentage": round(
                (missing / len(df) * 100) if len(df) else 0,
                2,
            ),
            "unique": int(series.nunique(dropna=True)),
        }

        if pd.api.types.is_numeric_dtype(series):
            item["statistics"] = {
                "mean": round(float(series.mean()), 6)
                if series.notna().any()
                else None,
                "median": round(float(series.median()), 6)
                if series.notna().any()
                else None,
                "std": round(float(series.std()), 6)
                if series.notna().sum() > 1
                else None,
                "min": round(float(series.min()), 6)
                if series.notna().any()
                else None,
                "max": round(float(series.max()), 6)
                if series.notna().any()
                else None,
            }

        column_profiles.append(item)

    date_range = None
    first_date = None
    last_date = None
    frequency = None

    if date_columns:
        date_col = date_columns[0]
        dates = pd.to_datetime(
            df[date_col],
            errors="coerce",
            format="mixed",
        ).dropna()

        if not dates.empty:
            dates = dates.sort_values()
            first_date = dates.iloc[0].strftime("%Y-%m-%d")
            last_date = dates.iloc[-1].strftime("%Y-%m-%d")
            date_range = f"{first_date} – {last_date}"

            if len(dates) >= 3:
                delta_days = dates.diff().dt.days.dropna()
                median_days = float(delta_days.median())

                if 27 <= median_days <= 32:
                    frequency = "MONTHLY"
                elif 6 <= median_days <= 8:
                    frequency = "WEEKLY"
                elif 350 <= median_days <= 380:
                    frequency = "YEARLY"
                elif 0.5 <= median_days <= 2:
                    frequency = "DAILY"
                else:
                    frequency = "IRREGULAR"

    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    issues = []

    if missing_cells:
        issues.append("Missing values detected")

    if duplicate_rows:
        issues.append("Duplicate rows detected")

    if not date_columns:
        issues.append("No date column was confidently detected")

    quality_status = "GOOD" if not issues else "ATTENTION"

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(c) for c in df.columns],
        "numeric_columns": numeric_columns,
        "date_columns": date_columns,
        "missing_cells": missing_cells,
        "missing_columns": missing_columns,
        "duplicate_rows": duplicate_rows,
        "date_range": date_range,
        "first_date": first_date,
        "last_date": last_date,
        "frequency": frequency,
        "quality_status": quality_status,
        "quality_issues": issues,
        "column_profiles": column_profiles,
    }


def prepare_series(
    df: pd.DataFrame,
    date_column: str,
    target_column: str,
):
    if date_column not in df.columns:
        raise ValueError(f"Date column '{date_column}' was not found.")

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' was not found.")

    work = df[[date_column, target_column]].copy()

    work[date_column] = pd.to_datetime(
        work[date_column],
        errors="coerce",
        format="mixed",
    )

    work[target_column] = pd.to_numeric(
        work[target_column],
        errors="coerce",
    )

    work = work.dropna()
    work = work.sort_values(date_column)
    work = work.drop_duplicates(
        subset=[date_column],
        keep="last",
    )

    if len(work) < 20:
        raise ValueError(
            "At least 20 valid time-series observations are required."
        )

    return work


def next_dates(last_date, horizon):
    last_date = pd.Timestamp(last_date)

    # Monthly is the primary forecasting use case.
    return pd.date_range(
        last_date + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq="MS",
    )


def metric_values(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    error = predicted - actual

    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(np.mean(error**2)))

    denominator = np.where(
        np.abs(actual) < 1e-9,
        np.nan,
        np.abs(actual),
    )

    mape = float(
        np.nanmean(np.abs(error) / denominator) * 100
    )

    smape = float(
        np.mean(
            2
            * np.abs(error)
            / np.maximum(
                np.abs(actual) + np.abs(predicted),
                1e-9,
            )
        )
        * 100
    )

    return {
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "smape": smape,
    }


# ============================================================
# MODEL HELPERS
# ============================================================

def forecast_tesm(series, horizon):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    values = pd.Series(series, dtype=float)

    seasonal_periods = 12 if len(values) >= 24 else None

    if seasonal_periods:
        model = ExponentialSmoothing(
            values,
            trend="add",
            seasonal="add",
            seasonal_periods=12,
            initialization_method="estimated",
        ).fit(optimized=True)
    else:
        model = ExponentialSmoothing(
            values,
            trend="add",
            initialization_method="estimated",
        ).fit(optimized=True)

    forecast = model.forecast(horizon)

    return (
        np.asarray(forecast, dtype=float),
        {
            "name": "TESM / Holt-Winters",
            "type": "Exponential Smoothing",
            "observations": len(values),
            "parameters": {
                "trend": "additive",
                "seasonality": "additive"
                if seasonal_periods
                else "none",
                "seasonal_periods": seasonal_periods,
                "alpha": getattr(
                    model.params,
                    "get",
                    lambda *_: None,
                )("smoothing_level"),
                "beta": getattr(
                    model.params,
                    "get",
                    lambda *_: None,
                )("smoothing_trend"),
                "gamma": getattr(
                    model.params,
                    "get",
                    lambda *_: None,
                )("smoothing_seasonal"),
            },
        },
    )


def forecast_sarima(series, horizon, exog=None):
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    values = pd.Series(series, dtype=float)

    model = SARIMAX(
        values,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12)
        if len(values) >= 36
        else (0, 0, 0, 0),
        exog=exog,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False)

    future_exog = None

    if exog is not None:
        last_value = float(exog.iloc[-1])
        future_exog = pd.Series(
            [last_value] * horizon,
            dtype=float,
        )

    result = model.get_forecast(
        steps=horizon,
        exog=future_exog,
    )

    forecast = np.asarray(
        result.predicted_mean,
        dtype=float,
    )

    confidence = result.conf_int(alpha=0.05)

    confidence_array = np.asarray(
        confidence,
        dtype=float,
    )

    lower = confidence_array[:, 0]
    upper = confidence_array[:, 1]
    return forecast, lower, upper, {
        "name": "SARIMA",
        "type": "SARIMA(1,1,1)(1,1,1,12)",
        "observations": len(values),
        "parameters": {
            "order": [1, 1, 1],
            "seasonal_order": [1, 1, 1, 12],
        },
        "aic": float(model.aic),
        "bic": float(model.bic),
    }


def make_ml_features(values):
    frame = pd.DataFrame({"target": values})

    for lag in [1, 2, 3, 6, 12]:
        frame[f"lag_{lag}"] = frame["target"].shift(lag)

    for window in [3, 6, 12]:
        shifted = frame["target"].shift(1)
        frame[f"rolling_mean_{window}"] = (
            shifted.rolling(window).mean()
        )
        frame[f"rolling_std_{window}"] = (
            shifted.rolling(window).std()
        )

    frame["month_number"] = np.arange(len(frame)) % 12 + 1
    frame["month_sin"] = np.sin(
        2 * np.pi * frame["month_number"] / 12
    )
    frame["month_cos"] = np.cos(
        2 * np.pi * frame["month_number"] / 12
    )

    frame["year_number"] = (
        np.arange(len(frame)) // 12
    )

    return frame


def recursive_ml_forecast(
    values,
    horizon,
    model_type,
):
    from sklearn.ensemble import RandomForestRegressor

    history = list(
        pd.Series(values, dtype=float).tolist()
    )

    frame = make_ml_features(history).dropna()

    feature_columns = [
        column
        for column in frame.columns
        if column != "target"
    ]

    X = frame[feature_columns]
    y = frame["target"]

    if model_type == "random_forest":
        model = RandomForestRegressor(
            n_estimators=500,
            max_features=1.0,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        )

    elif model_type == "xgboost":
        try:
            from xgboost import XGBRegressor

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
        except ImportError as exc:
            raise RuntimeError(
                "XGBoost is not installed in the active Python environment."
            ) from exc

    else:
        raise ValueError(
            f"Unsupported ML model: {model_type}"
        )

    model.fit(X, y)

    predictions = []

    for _ in range(horizon):
        current = make_ml_features(history)
        latest = current.iloc[[-1]][feature_columns]

        prediction = float(
            model.predict(latest)[0]
        )

        predictions.append(prediction)
        history.append(prediction)

    display_name = (
        "Random Forest"
        if model_type == "random_forest"
        else "XGBoost"
    )

    return np.asarray(predictions), {
        "name": display_name,
        "type": display_name,
        "observations": len(values),
        "parameters": {
            "feature_count": len(feature_columns),
            "recursive_forecast": True,
            "random_state": 42,
        },
        "feature_names": feature_columns,
        "estimator": model,
    }


def forecast_deep_learning(values, horizon, model_type):
    try:
        tf = importlib.import_module("tensorflow")
        keras = tf.keras
        Sequential = keras.Sequential
        EarlyStopping = keras.callbacks.EarlyStopping
        Input = keras.layers.Input
        LSTM = keras.layers.LSTM
        GRU = keras.layers.GRU
        Dense = keras.layers.Dense
        Dropout = keras.layers.Dropout
    except (ImportError, AttributeError) as exc:
        raise RuntimeError(
            "TensorFlow is not available in the active Python environment."
        ) from exc

    tf.random.set_seed(42)
    np.random.seed(42)

    values = np.asarray(values, dtype=float)

    sequence_length = 12

    if len(values) <= sequence_length + 5:
        raise ValueError(
            "Deep-learning forecasting requires more historical observations."
        )

    minimum = float(values.min())
    maximum = float(values.max())
    scale = maximum - minimum

    if scale == 0:
        scale = 1.0

    scaled = (values - minimum) / scale

    X = []
    y = []

    for index in range(
        sequence_length,
        len(scaled),
    ):
        X.append(
            scaled[
                index - sequence_length:index
            ]
        )
        y.append(scaled[index])

    X = np.asarray(X).reshape(
        -1,
        sequence_length,
        1,
    )
    y = np.asarray(y)

    model = Sequential(
        [
            Input(
                shape=(sequence_length, 1)
            ),
            (
                LSTM(64, return_sequences=True)
                if model_type == "lstm"
                else GRU(64, return_sequences=True)
            ),
            Dropout(0.2),
            (
                LSTM(32)
                if model_type == "lstm"
                else GRU(32)
            ),
            Dropout(0.2),
            Dense(16, activation="relu"),
            Dense(1),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="mse",
        metrics=["mae"],
    )

    callback = EarlyStopping(
        monitor="loss",
        patience=12,
        restore_best_weights=True,
    )

    model.fit(
        X,
        y,
        epochs=80,
        batch_size=8,
        shuffle=False,
        verbose=0,
        callbacks=[callback],
    )

    history = list(scaled)

    predictions_scaled = []

    for _ in range(horizon):
        sequence = np.asarray(
            history[-sequence_length:]
        ).reshape(
            1,
            sequence_length,
            1,
        )

        prediction = float(
            model.predict(
                sequence,
                verbose=0,
            )[0][0]
        )

        predictions_scaled.append(prediction)
        history.append(prediction)

    predictions = (
        np.asarray(predictions_scaled) * scale
        + minimum
    )

    display_name = (
        "LSTM"
        if model_type == "lstm"
        else "GRU"
    )

    return predictions, {
        "name": display_name,
        "type": display_name,
        "observations": len(values),
        "parameters": {
            "sequence_length": sequence_length,
            "units": [64, 32],
            "dropout": 0.2,
            "epochs": 80,
            "batch_size": 8,
        },
    }


# ============================================================
# AUTHENTICATION / DATABASE API
# ============================================================

@app.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    confirm_password = str(payload.get("confirm_password", payload.get("confirmPassword", "")))

    if not name:
        return error_response("Name is required.", 400)
    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return error_response("A valid email address is required.", 400)
    if len(password) < 8:
        return error_response("Password must contain at least 8 characters.", 400)
    if not re.search(r"[A-Z]", password):
        return error_response("Password must contain at least one uppercase letter.", 400)
    if not re.search(r"[a-z]", password):
        return error_response("Password must contain at least one lowercase letter.", 400)
    if not re.search(r"\d", password):
        return error_response("Password must contain at least one number.", 400)
    if not re.search(r"[^A-Za-z0-9]", password):
        return error_response("Password must contain at least one special character.", 400)
    if password != confirm_password:
        return error_response("Passwords do not match.", 400)

    if users_collection.find_one({"email": email}):
        return error_response("An account with this email already exists.", 409)

    now = datetime.now().isoformat()
    result = users_collection.insert_one(
        {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": "user",
            "is_active": True,
            "created_at": now,
            "last_login_at": None,
        }
    )
    log_activity(result.inserted_id, "REGISTER", "user", result.inserted_id)

    return jsonify(
        {
            "success": True,
            "message": "Account created successfully. Please sign in.",
        }
    ), 201


@app.post("/api/auth/forgot-password")
def forgot_password():
    """Start a password reset for either a user or an administrator.

    The response intentionally does not reveal whether an email exists.
    In local development, PASSWORD_RESET_DEV_MODE exposes the one-time code
    so the flow can be tested without an SMTP server.
    """
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()

    generic_message = (
        "If an account exists for this email, a password reset code has "
        "been generated. Check your email."
    )

    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"success": True, "message": generic_message})

    user = users_collection.find_one({"email": email})

    if user is None or not user.get("is_active", False):
        return jsonify({"success": True, "message": generic_message})

    code = f"{secrets.randbelow(1000000):06d}"
    now = datetime.now()
    expires_at = now.timestamp() + (PASSWORD_RESET_TTL_MINUTES * 60)

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password_reset_code_hash": generate_password_hash(code),
                "password_reset_expires_at": expires_at,
                "password_reset_attempts": 0,
                "password_reset_requested_at": now.isoformat(),
            }
        },
    )

    email_sent = False
    try:
        email_sent = send_password_reset_email(email, code)
    except Exception as exc:
        app.logger.warning("Password reset email could not be sent: %s", exc)

    log_activity(
        user["_id"],
        "PASSWORD_RESET_REQUESTED",
        "user",
        user["_id"],
        {"email_sent": email_sent},
    )

    response = {"success": True, "message": generic_message}

    if PASSWORD_RESET_DEV_MODE and not email_sent:
        response["dev_reset_code"] = code
        response["message"] = (
            "Password reset code generated. Development mode is enabled; "
            "use the displayed code to continue."
        )

    return jsonify(response)


@app.post("/api/auth/reset-password")
def reset_password():
    """Complete a password reset using the short-lived one-time code."""
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    code = str(payload.get("code", "")).strip()
    password = str(payload.get("password", ""))
    confirm_password = str(
        payload.get("confirm_password", payload.get("confirmPassword", ""))
    )

    if not email or not code:
        return error_response("Email and reset code are required.", 400)

    if len(code) != 6 or not code.isdigit():
        return error_response("Enter the 6-digit reset code.", 400)

    if len(password) < 8:
        return error_response("Password must contain at least 8 characters.", 400)
    if not re.search(r"[A-Z]", password):
        return error_response("Password must contain at least one uppercase letter.", 400)
    if not re.search(r"[a-z]", password):
        return error_response("Password must contain at least one lowercase letter.", 400)
    if not re.search(r"\d", password):
        return error_response("Password must contain at least one number.", 400)
    if not re.search(r"[^A-Za-z0-9]", password):
        return error_response("Password must contain at least one special character.", 400)
    if password != confirm_password:
        return error_response("Passwords do not match.", 400)

    user = users_collection.find_one({"email": email})

    if user is None or not user.get("is_active", False):
        return error_response("Invalid or expired reset code.", 400)

    expires_at = float(user.get("password_reset_expires_at", 0) or 0)
    attempts = int(user.get("password_reset_attempts", 0) or 0)

    if not user.get("password_reset_code_hash") or expires_at < datetime.now().timestamp():
        return error_response("Invalid or expired reset code.", 400)

    if attempts >= 5:
        return error_response("Too many reset attempts. Request a new code.", 429)

    if not check_password_hash(user["password_reset_code_hash"], code):
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$inc": {"password_reset_attempts": 1}},
        )
        return error_response("Invalid or expired reset code.", 400)

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password_hash": generate_password_hash(password),
                "password_changed_at": datetime.now().isoformat(),
            },
            "$unset": {
                "password_reset_code_hash": "",
                "password_reset_expires_at": "",
                "password_reset_attempts": "",
                "password_reset_requested_at": "",
            },
        },
    )

    log_activity(user["_id"], "PASSWORD_RESET_COMPLETED", "user", user["_id"])

    return jsonify({
        "success": True,
        "message": "Password reset successfully. Please sign in with your new password.",
    })


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        return error_response("Email and password are required.", 400)

    user = users_collection.find_one({"email": email})

    if user is None or not user.get("is_active", False):
        if user:
            log_activity(user["_id"], "LOGIN_FAILED", "user", user["_id"], {"reason": "inactive_account"})
        return error_response("Invalid email or password.", 401)

    if not check_password_hash(user["password_hash"], password):
        log_activity(user["_id"], "LOGIN_FAILED", "user", user["_id"], {"reason": "invalid_password"})
        return error_response("Invalid email or password.", 401)

    now = datetime.now().isoformat()
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": now}},
    )

    session.clear()
    session["user_id"] = str(user["_id"])
    log_activity(user["_id"], "LOGIN_SUCCESS", "user", user["_id"])

    user["last_login_at"] = now
    return jsonify({"success": True, "user": serialize_user(user)})


@app.get("/api/auth/me")
def current_user():
    user = get_current_user_record()
    if user is None:
        return error_response("Not authenticated.", 401)
    return jsonify({"success": True, "user": serialize_user(user)})


@app.post("/api/auth/logout")
def logout():
    user = get_current_user_record()
    if user is not None:
        log_activity(user["_id"], "LOGOUT", "user", user["_id"])
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})


@app.post("/api/database/status")
@app.get("/api/database/status")
@require_auth
def database_status():
    try:
        mongo_client.admin.command("ping")
        return jsonify(
            {
                "success": True,
                "database": {
                    "connected": True,
                    "engine": "MongoDB",
                    "database_name": MONGO_DB_NAME,
                    "server": MONGO_URI,
                    "collections": db.list_collection_names(),
                },
            }
        )
    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "database": {
                    "connected": False,
                    "engine": "MongoDB",
                    "database_name": MONGO_DB_NAME,
                    "error": str(exc),
                },
            }
        ), 500


# ============================================================
# AUTHORIZATION TEST / ADMIN FOUNDATION
# ============================================================

@app.get("/api/admin/access")
@require_admin
def admin_access():
    """Confirm that the current session has administrator privileges."""
    user = get_current_user_record()

    return jsonify(
        {
            "success": True,
            "authorized": True,
            "role": "admin",
            "user": serialize_user(user),
        }
    )




# ============================================================
# ADMINISTRATION / OVERSIGHT
# ============================================================

def _admin_user_summary(user):
    return {
        "id": serialize_object_id(user.get("_id")),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "user"),
        "is_active": bool(user.get("is_active", True)),
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
    }


@app.get("/api/admin/overview")
@require_admin
def admin_overview():
    """Return a controlled administrative overview without password data."""
    try:
        current_admin = get_current_user_record()
        total_users = users_collection.count_documents({})
        active_users = users_collection.count_documents({"is_active": True})
        inactive_users = users_collection.count_documents({"is_active": False})
        total_admins = users_collection.count_documents({"role": "admin"})
        total_datasets = datasets_collection.count_documents({})
        total_reports = report_history_collection.count_documents({})
        total_model_runs = model_runs_collection.count_documents({})

        recent_users = [
            _admin_user_summary(user)
            for user in users_collection.find({}).sort("created_at", DESCENDING).limit(12)
        ]

        recent_activity = []
        activity_cursor = activity_logs_collection.find({}).sort("created_at", DESCENDING).limit(20)
        for item in activity_cursor:
            user = None
            user_id = item.get("user_id")
            if isinstance(user_id, ObjectId):
                user = users_collection.find_one(
                    {"_id": user_id},
                    {"name": 1, "email": 1, "role": 1},
                )
            recent_activity.append(
                {
                    "id": serialize_object_id(item.get("_id")),
                    "action": item.get("action", ""),
                    "resource_type": item.get("resource_type"),
                    "resource_id": item.get("resource_id"),
                    "created_at": item.get("created_at"),
                    "ip_address": item.get("ip_address"),
                    "user": {
                        "name": user.get("name", "") if user else "System",
                        "email": user.get("email", "") if user else "",
                        "role": user.get("role", "system") if user else "system",
                    },
                }
            )

        recent_reports = []
        for item in report_history_collection.find({}).sort("created_at", DESCENDING).limit(12):
            owner = None
            owner_id = item.get("user_id")
            if isinstance(owner_id, ObjectId):
                owner = users_collection.find_one(
                    {"_id": owner_id},
                    {"name": 1, "email": 1, "role": 1},
                )
            recent_reports.append(
                {
                    "report_id": item.get("report_id"),
                    "created_at": item.get("created_at"),
                    "dataset_id": item.get("dataset_id"),
                    "dataset_filename": item.get("dataset_filename"),
                    "owner": {
                        "name": owner.get("name", "") if owner else "Unknown",
                        "email": owner.get("email", "") if owner else "",
                        "role": owner.get("role", "user") if owner else "user",
                    },
                    "review_status": item.get("review_status", "Pending administrative review"),
                }
            )

        return jsonify(
            {
                "success": True,
                "administrator": _admin_user_summary(current_admin),
                "summary": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": inactive_users,
                    "total_admins": total_admins,
                    "total_datasets": total_datasets,
                    "total_reports": total_reports,
                    "total_model_runs": total_model_runs,
                    "collections": db.list_collection_names(),
                },
                "users": recent_users,
                "activity": recent_activity,
                "reports": recent_reports,
            }
        )
    except Exception as exc:
        app.logger.exception("Administrative overview error")
        return error_response(f"Unable to load administrative information: {exc}", 500)


@app.post("/api/admin/users/<user_id>/status")
@require_admin
def admin_user_status(user_id):
    """Activate or deactivate a normal user account; administrators are protected."""
    current_admin = get_current_user_record()
    payload = request.get_json(silent=True) or {}
    requested_active = payload.get("is_active")

    if not isinstance(requested_active, bool):
        return error_response("is_active must be true or false.", 400)

    try:
        target_id = ObjectId(user_id)
    except Exception:
        return error_response("Invalid user identifier.", 400)

    target = users_collection.find_one({"_id": target_id})
    if target is None:
        return error_response("User account was not found.", 404)

    if target.get("role") == "admin":
        return error_response(
            "Administrator accounts cannot be activated or deactivated from this control.",
            403,
        )

    users_collection.update_one(
        {"_id": target_id},
        {"$set": {"is_active": requested_active}},
    )

    action = "ACCOUNT_ACTIVATED" if requested_active else "ACCOUNT_DEACTIVATED"
    log_activity(
        current_admin["_id"],
        action,
        "user",
        target_id,
        {"target_email": target.get("email", "")},
    )

    return jsonify(
        {
            "success": True,
            "message": "User account status updated.",
            "user": _admin_user_summary(
                users_collection.find_one({"_id": target_id})
            ),
        }
    )


@app.get("/api/admin/activity")
@require_admin
def admin_activity():
    """Return recent audit events for administrative review."""
    limit = request.args.get("limit", "50")
    try:
        limit = max(1, min(int(limit), 200))
    except ValueError:
        limit = 50

    records = []
    for item in activity_logs_collection.find({}).sort("created_at", DESCENDING).limit(limit):
        user = None
        if isinstance(item.get("user_id"), ObjectId):
            user = users_collection.find_one(
                {"_id": item["user_id"]},
                {"name": 1, "email": 1, "role": 1},
            )
        records.append(
            {
                "id": serialize_object_id(item.get("_id")),
                "action": item.get("action"),
                "resource_type": item.get("resource_type"),
                "resource_id": item.get("resource_id"),
                "created_at": item.get("created_at"),
                "ip_address": item.get("ip_address"),
                "user": {
                    "name": user.get("name", "") if user else "System",
                    "email": user.get("email", "") if user else "",
                    "role": user.get("role", "system") if user else "system",
                },
                "details": item.get("details", {}),
            }
        )

    return jsonify({"success": True, "activity": records})


# ============================================================
# AUDIT DECORATORS FOR MODEL / REPORT ACTIVITY
# ============================================================

def audit_model_run(model_name):
    """Record model execution without exposing sensitive user data."""
    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs):
            response = view_function(*args, **kwargs)
            try:
                payload = request.get_json(silent=True) or {}
                user_id = session.get("user_id")
                dataset_id = payload.get("dataset_id") or payload.get("active_dataset_id")
                if user_id:
                    log_activity(user_id, "MODEL_RUN", "model", model_name, {"dataset_id": dataset_id, "model": model_name})
            except Exception:
                app.logger.exception("Model audit logging failed")
            return response
        return wrapped_view
    return decorator


def audit_report_download(report_type):
    """Record report downloads after the protected endpoint is reached."""
    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(report_id, *args, **kwargs):
            response = view_function(report_id, *args, **kwargs)
            try:
                user_id = session.get("user_id")
                if user_id:
                    log_activity(user_id, "REPORT_DOWNLOADED", "report", report_id, {"format": report_type})
            except Exception:
                app.logger.exception("Report download audit logging failed")
            return response
        return wrapped_view
    return decorator


# ============================================================
# UPLOAD / PROFILE
# ============================================================

@app.get("/")
def root():
    return jsonify(
        {
            "status": "success",
            "message": "ForecastIQ API is running",
        }
    )


@app.get("/api/health")
def health():
    return jsonify(
        {
            "success": True,
            "status": "healthy",
            "application": "ForecastIQ",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.post("/api/upload")
@require_auth
def upload_dataset():
    try:
        if "file" not in request.files:
            return error_response(
                "No dataset file was uploaded."
            )

        file = request.files["file"]

        if not file.filename:
            return error_response(
                "The uploaded file has no filename."
            )

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            return error_response(
                "Only CSV, XLSX and XLS files are supported."
            )

        dataset_id = uuid.uuid4().hex
        safe_filename = clean_name(file.filename)
        save_path = UPLOAD_FOLDER / f"{dataset_id}{extension}"

        file.save(save_path)

        df = read_dataset(save_path)

        if df.empty:
            save_path.unlink(missing_ok=True)
            return error_response(
                "The uploaded dataset is empty."
            )

        profile = profile_dataset(df)

        date_suggestions = profile["date_columns"]

        target_suggestions = [
            column
            for column in profile["numeric_columns"]
            if column.lower() not in {"year", "month"}
        ]

        preview_df = df.head(10).copy()
        preview_df = preview_df.astype(object)
        preview_df = preview_df.where(pd.notna(preview_df), None)
        preview = preview_df.to_dict(orient="records")

        return jsonify(
            {
                "success": True,
                "dataset": {
                    "id": dataset_id,
                    "filename": safe_filename,
                    "profile": json_safe(profile),
                    "preview": json_safe(preview),
                    "date_suggestions": date_suggestions,
                    "target_suggestions": target_suggestions,
                },
            }
        )

    except Exception as exc:
        return error_response(
            f"Dataset upload failed: {exc}",
            500,
        )


# ============================================================
# CLEANING
# ============================================================

@app.post("/api/clean")
@require_auth
def clean_dataset():
    try:
        payload = request.get_json(silent=True) or {}

        dataset_id = payload.get("dataset_id")
        date_column = payload.get("date_column")
        target_column = payload.get("target_column")

        if not dataset_id:
            return error_response(
                "Dataset ID is required."
            )

        path = resolve_dataset(dataset_id)

        if path is None:
            return error_response(
                "The requested dataset could not be found."
            )

        df = read_dataset(path)
        before = profile_dataset(df)

        missing_method = payload.get(
            "missing_method",
            "none",
        )
        duplicate_method = payload.get(
            "duplicate_method",
            "keep",
        )
        outlier_method = payload.get(
            "outlier_method",
            "none",
        )
        transformation = payload.get(
            "transformation",
            "none",
        )

        if duplicate_method == "remove":
            df = df.drop_duplicates()

        if missing_method == "drop":
            df = df.dropna()
        elif missing_method == "ffill":
            df = df.ffill()
        elif missing_method == "bfill":
            df = df.bfill()
        elif missing_method == "interpolate":
            numeric_columns = df.select_dtypes(
                include=np.number
            ).columns

            df[numeric_columns] = (
                df[numeric_columns]
                .interpolate()
                .ffill()
                .bfill()
            )

        if (
            target_column
            and target_column in df.columns
        ):
            numeric_target = pd.to_numeric(
                df[target_column],
                errors="coerce",
            )

            if outlier_method == "iqr_cap":
                q1 = numeric_target.quantile(0.25)
                q3 = numeric_target.quantile(0.75)
                iqr = q3 - q1

                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr

                df[target_column] = numeric_target.clip(
                    lower,
                    upper,
                )

            elif outlier_method == "robust_zscore_cap":
                median = numeric_target.median()
                mad = np.median(
                    np.abs(
                        numeric_target.dropna()
                        - median
                    )
                )

                if mad > 0:
                    robust_z = (
                        0.6745
                        * (numeric_target - median)
                        / mad
                    )

                    df[target_column] = np.where(
                        robust_z > 3,
                        median + 3 * mad / 0.6745,
                        np.where(
                            robust_z < -3,
                            median - 3 * mad / 0.6745,
                            numeric_target,
                        ),
                    )

            if transformation == "log1p":
                minimum = float(
                    pd.to_numeric(
                        df[target_column],
                        errors="coerce",
                    ).min()
                )

                shift = (
                    abs(minimum) + 1
                    if minimum <= -1
                    else 0
                )

                df[target_column] = np.log1p(
                    pd.to_numeric(
                        df[target_column],
                        errors="coerce",
                    )
                    + shift
                )

        if date_column and date_column in df.columns:
            df[date_column] = pd.to_datetime(
                df[date_column],
                errors="coerce",
                format="mixed",
            )
            df = df.sort_values(date_column)

        after = profile_dataset(df)

        cleaned_id = uuid.uuid4().hex
        output_path = (
            PROCESSED_FOLDER
            / f"{cleaned_id}.csv"
        )

        df.to_csv(
            output_path,
            index=False,
        )

        preview_df = df.head(10).copy()
        preview_df = preview_df.astype(object)
        preview_df = preview_df.where(pd.notna(preview_df), None)
        preview = preview_df.to_dict(orient="records")

        return jsonify(
            {
                "success": True,
                "dataset": {
                    "dataset_id": cleaned_id,
                    "source_dataset_id": dataset_id,
                    "filename": output_path.name,
                    "profile": json_safe(after),
                    "preview": json_safe(preview),
                    "before": json_safe(before),
                    "after": json_safe(after),
                    "changes": {
                        "rows_before": before["rows"],
                        "rows_after": after["rows"],
                        "missing_before": before[
                            "missing_cells"
                        ],
                        "missing_after": after[
                            "missing_cells"
                        ],
                        "duplicates_before": before[
                            "duplicate_rows"
                        ],
                        "duplicates_after": after[
                            "duplicate_rows"
                        ],
                    },
                },
            }
        )

    except Exception as exc:
        return error_response(
            f"Dataset cleaning failed: {exc}",
            500,
        )


# ============================================================
# EXPLORATION
# ============================================================

@app.post("/api/explore")
@require_auth
def explore_dataset():
    try:
        payload = request.get_json(silent=True) or {}

        dataset_id = payload.get("dataset_id")
        date_column = payload.get("date_column")
        target_column = payload.get("target_column")

        path = resolve_dataset(dataset_id)

        if path is None:
            return error_response(
                "The active dataset could not be found."
            )

        df = read_dataset(path)
        work = prepare_series(
            df,
            date_column,
            target_column,
        )

        dates = work[date_column]
        values = work[target_column].astype(float)

        x = np.arange(len(values))

        slope = float(
            np.polyfit(
                x,
                values.to_numpy(),
                1,
            )[0]
        )

        if slope > 0.05:
            trend = "Increasing"
        elif slope < -0.05:
            trend = "Decreasing"
        else:
            trend = "Stable"

        monthly = (
            work.assign(
                month=dates.dt.month
            )
            .groupby("month")[target_column]
            .mean()
            .reset_index()
        )

        try:
            from statsmodels.tsa.stattools import (
                adfuller,
                acf,
                pacf,
            )

            adf_result = adfuller(
                values,
                autolag="AIC",
            )

            difference = values.diff().dropna()

            diff_result = adfuller(
                difference,
                autolag="AIC",
            )

            max_lag = min(
                24,
                max(1, len(values) // 3),
            )

            acf_values = acf(
                values,
                nlags=max_lag,
                fft=True,
            )

            pacf_lag = min(
                24,
                max(1, len(values) // 2 - 1),
            )

            pacf_values = pacf(
                values,
                nlags=pacf_lag,
                method="ywm",
            )

        except Exception:
            adf_result = [np.nan, np.nan, 0, 0]
            diff_result = [np.nan, np.nan, 0, 0]
            acf_values = np.array([1.0])
            pacf_values = np.array([1.0])

        analysis = {
            "rows_analyzed": len(work),
            "first_date": dates.iloc[0].strftime(
                "%Y-%m-%d"
            ),
            "last_date": dates.iloc[-1].strftime(
                "%Y-%m-%d"
            ),
            "trend": trend,
            "trend_slope": slope,
            "statistics": {
                "count": len(values),
                "mean": float(values.mean()),
                "std": float(values.std()),
                "min": float(values.min()),
                "max": float(values.max()),
                "median": float(values.median()),
            },
            "time_series": [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "value": float(value),
                }
                for date, value in zip(
                    dates,
                    values,
                )
            ],
            "monthly_seasonality": [
                {
                    "month": int(row["month"]),
                    "average": float(row[target_column]),
                }
                for _, row in monthly.iterrows()
            ],
            "adf": {
                "statistic": float(adf_result[0]),
                "p_value": float(adf_result[1]),
                "lags": int(adf_result[2]),
                "observations": int(adf_result[3]),
                "stationary": bool(
                    adf_result[1] < 0.05
                ),
            },
            "differenced_adf": {
                "statistic": float(diff_result[0]),
                "p_value": float(diff_result[1]),
                "stationary": bool(
                    diff_result[1] < 0.05
                ),
            },
            "acf": [
                {
                    "lag": int(index),
                    "value": float(value),
                }
                for index, value in enumerate(
                    acf_values
                )
            ],
            "pacf": [
                {
                    "lag": int(index),
                    "value": float(value),
                }
                for index, value in enumerate(
                    pacf_values
                )
            ],
        }

        return jsonify(
            {
                "success": True,
                "analysis": json_safe(analysis),
            }
        )

    except Exception as exc:
        return error_response(
            f"Exploration failed: {exc}",
            500,
        )


# ============================================================
# ANOMALY DETECTION
# ============================================================

def pettitt_test(values):
    """Return a robust Pettitt change-point estimate.

    Uses the rank formulation of the Pettitt statistic rather than
    constructing an NxN comparison matrix. This keeps memory usage
    reasonable for large uploaded datasets.
    """
    numeric = pd.to_numeric(pd.Series(values), errors="coerce")
    numeric = numeric.replace([np.inf, -np.inf], np.nan).dropna()
    values_array = numeric.to_numpy(dtype=float)

    n = len(values_array)
    if n < 12:
        return None

    ranks = pd.Series(values_array).rank(method="average").to_numpy()
    time_index = np.arange(1, n + 1, dtype=float)

    # Pettitt U_t = 2 * sum(ranks_1:t) - t * (n + 1)
    u_values = (
        2.0 * np.cumsum(ranks)
        - time_index * (n + 1.0)
    )

    best_position = int(np.argmax(np.abs(u_values)))
    k = best_position + 1
    u = float(abs(u_values[best_position]))

    p_value = min(
        1.0,
        2.0 * math.exp(
            (-6.0 * u * u) / (n**3 + n**2)
        ),
    )

    before = values_array[:k]
    after = values_array[k:]

    if len(before) == 0 or len(after) == 0:
        return None

    mean_change = float(
        np.mean(after) - np.mean(before)
    )

    return {
        "index": k,
        "p_value": float(p_value),
        "mean_change": mean_change,
    }


def anomaly_analysis(work):
    """Detect statistical and Isolation Forest anomalies safely."""
    analysis = work.copy()

    analysis["date"] = pd.to_datetime(
        analysis["date"],
        errors="coerce",
        format="mixed",
    )
    analysis["value"] = pd.to_numeric(
        analysis["value"],
        errors="coerce",
    )

    analysis = analysis.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna(subset=["date", "value"])

    analysis = (
        analysis
        .sort_values("date")
        .drop_duplicates(
            subset=["date"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    if len(analysis) < 12:
        raise ValueError(
            "At least 12 valid time-series observations are required "
            "for anomaly analysis."
        )

    values = analysis["value"].astype(float)

    # --------------------------------------------------------
    # Robust rolling baseline
    # --------------------------------------------------------
    rolling_median = (
        values.rolling(
            window=12,
            center=True,
            min_periods=3,
        )
        .median()
        .bfill()
        .ffill()
    )

    residual = values - rolling_median

    residual_median = float(
        residual.median()
    )

    mad = float(
        np.median(
            np.abs(
                residual.to_numpy(dtype=float)
                - residual_median
            )
        )
    )

    if not np.isfinite(mad) or mad < 1e-9:
        fallback_std = float(
            residual.std()
        )
        mad = (
            fallback_std
            if np.isfinite(fallback_std) and fallback_std > 1e-9
            else 1.0
        )

    robust_z = (
        0.6745
        * (residual - residual_median)
        / mad
    )

    robust_z = robust_z.replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0.0)

    statistical = (
        robust_z.abs() >= 3.0
    ).astype(bool)

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------
    isolation = np.zeros(
        len(analysis),
        dtype=bool,
    )

    try:
        from sklearn.ensemble import IsolationForest

        if len(analysis) >= 20:
            contamination = min(
                0.10,
                max(
                    0.02,
                    5.0 / len(analysis),
                ),
            )

            detector = IsolationForest(
                n_estimators=200,
                contamination=contamination,
                random_state=42,
                n_jobs=-1,
            )

            isolation = (
                detector.fit_predict(
                    values.to_numpy(
                        dtype=float
                    ).reshape(-1, 1)
                ) == -1
            ).astype(bool)

    except Exception:
        # Statistical detection remains available even when
        # Isolation Forest cannot be executed.
        isolation = np.zeros(
            len(analysis),
            dtype=bool,
        )

    combined = (
        statistical.to_numpy(dtype=bool)
        | isolation
    )

    analysis["residual"] = residual.to_numpy(
        dtype=float
    )
    analysis["robust_z_score"] = robust_z.to_numpy(
        dtype=float
    )
    analysis["statistical_anomaly"] = statistical.to_numpy(
        dtype=bool
    )
    analysis["isolation_forest_anomaly"] = isolation
    analysis["combined_anomaly"] = combined

    timeline = []

    detected = analysis.loc[
        analysis["combined_anomaly"]
    ]

    for _, row in detected.iterrows():
        z_score = float(
            row["robust_z_score"]
        )
        residual_value = float(
            row["residual"]
        )

        if abs(z_score) >= 5.0:
            severity = "HIGH"
        elif abs(z_score) >= 3.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        timeline.append(
            {
                "date": row["date"].strftime(
                    "%Y-%m-%d"
                ),
                "value": float(row["value"]),
                "residual": residual_value,
                "robust_z_score": z_score,
                "severity": severity,
                "direction": (
                    "Above expected"
                    if residual_value > 0
                    else "Below expected"
                ),
                "statistical_anomaly": bool(
                    row["statistical_anomaly"]
                ),
                "isolation_forest_anomaly": bool(
                    row["isolation_forest_anomaly"]
                ),
            }
        )

    return analysis, timeline


@app.post("/api/anomalies")
@require_auth
def anomalies():
    """Run anomaly and structural-break analysis on the active dataset."""
    try:
        payload = request.get_json(
            silent=True
        ) or {}

        dataset_id = payload.get(
            "dataset_id"
        )

        if not dataset_id:
            return error_response(
                "Dataset ID is required. Upload a dataset before running anomaly analysis."
            )

        path = resolve_dataset(
            dataset_id
        )

        if path is None:
            return error_response(
                "The active dataset could not be found. Please upload the dataset again."
            )

        df = read_dataset(path)

        if df.empty:
            return error_response(
                "The active dataset is empty."
            )

        # ----------------------------------------------------
        # Resolve date column
        # ----------------------------------------------------
        date_column = payload.get(
            "date_column"
        )

        if (
            not date_column
            or date_column not in df.columns
        ):
            date_candidates = detect_date_columns(
                df
            )
            date_column = (
                date_candidates[0]
                if date_candidates
                else None
            )

        # ----------------------------------------------------
        # Resolve target column
        # ----------------------------------------------------
        target_column = payload.get(
            "target_column"
        )

        if (
            not target_column
            or target_column not in df.columns
        ):
            numeric_columns = [
                column
                for column in df.columns
                if pd.api.types.is_numeric_dtype(
                    df[column]
                )
            ]

            preferred_names = {
                "target",
                "index",
                "value",
                "output",
                "production",
                "sales",
                "demand",
                "quantity",
                "amount",
                "revenue",
                "price",
            }

            target_column = next(
                (
                    column
                    for column in numeric_columns
                    if str(column).strip().lower()
                    in preferred_names
                    and str(column).strip().lower()
                    not in {"year", "month"}
                ),
                None,
            )

            if target_column is None:
                target_column = next(
                    (
                        column
                        for column in numeric_columns
                        if str(column).strip().lower()
                        not in {"year", "month"}
                    ),
                    None,
                )

        if not date_column:
            return error_response(
                "A valid date column could not be detected. Select a date column in DATA."
            )

        if not target_column:
            return error_response(
                "A valid numeric target column could not be detected. Select a target column in DATA."
            )

        # ----------------------------------------------------
        # Prepare clean time series
        # ----------------------------------------------------
        work = prepare_series(
            df,
            date_column,
            target_column,
        ).rename(
            columns={
                date_column: "date",
                target_column: "value",
            }
        )

        if len(work) < 12:
            return error_response(
                "At least 12 valid observations are required for anomaly analysis."
            )

        # ----------------------------------------------------
        # Anomaly detection
        # ----------------------------------------------------
        result, timeline = anomaly_analysis(
            work
        )

        # ----------------------------------------------------
        # Structural break detection
        # ----------------------------------------------------
        break_result = pettitt_test(
            work["value"].to_numpy(
                dtype=float
            )
        )

        structural_breaks = []

        if (
            break_result is not None
            and break_result["p_value"] < 0.05
        ):
            break_index = min(
                max(
                    int(break_result["index"]),
                    0,
                ),
                len(work) - 1,
            )

            break_date = pd.Timestamp(
                work.iloc[break_index]["date"]
            )

            mean_change = float(
                break_result["mean_change"]
            )

            structural_breaks.append(
                {
                    "sector": "Uploaded Dataset",
                    "date": break_date.strftime(
                        "%B %Y"
                    ),
                    "change": round(
                        mean_change,
                        2,
                    ),
                    "direction": (
                        "Increase"
                        if mean_change > 0
                        else "Decrease"
                    ),
                    "p_value": float(
                        break_result["p_value"]
                    ),
                }
            )

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------
        total = int(len(timeline))
        high = int(
            sum(
                item["severity"] == "HIGH"
                for item in timeline
            )
        )
        medium = int(
            sum(
                item["severity"] == "MEDIUM"
                for item in timeline
            )
        )
        low = int(
            sum(
                item["severity"] == "LOW"
                for item in timeline
            )
        )

        sector_summary = [
            {
                "sector": "Uploaded Dataset",
                "observations": int(len(result)),
                "statistical_anomalies": int(
                    result[
                        "statistical_anomaly"
                    ].sum()
                ),
                "isolation_forest_anomalies": int(
                    result[
                        "isolation_forest_anomaly"
                    ].sum()
                ),
                "combined_anomalies": total,
            }
        ]

        response_data = {
            "success": True,
            "analysis": {
                "dataset_id": str(dataset_id),
                "date_column": str(date_column),
                "target_column": str(target_column),
                "summary": {
                    "total_anomalies": total,
                    "high": high,
                    "medium": medium,
                    "low": low,
                },
                "sector_summary": sector_summary,
                "timeline": timeline,
                "sectors": [
                    {
                        "sector": "Uploaded Dataset",
                        "count": total,
                    }
                ],
                "severity": [
                    {
                        "severity": "HIGH",
                        "count": high,
                    },
                    {
                        "severity": "MEDIUM",
                        "count": medium,
                    },
                    {
                        "severity": "LOW",
                        "count": low,
                    },
                ],
                "structural_breaks": structural_breaks,
            },
        }

        return jsonify(
            json_safe(response_data)
        )

    except ValueError as exc:
        return error_response(
            f"Anomaly analysis validation failed: {exc}",
            400,
        )
    except Exception as exc:
        app.logger.exception(
            "Anomaly analysis failed"
        )
        return error_response(
            f"Anomaly analysis failed: {exc}",
            500,
        )


# ============================================================
# MODEL ROUTES
# ============================================================

def model_request(model_name):
    payload = request.get_json(silent=True) or {}

    dataset_id = payload.get("dataset_id")

    if not dataset_id:
        raise ValueError(
            "Dataset ID is required. Upload a dataset first."
        )

    path = resolve_dataset(dataset_id)

    if path is None:
        raise ValueError(
            "The active dataset could not be found."
        )

    df = read_dataset(path)

    date_column = payload.get("date_column")
    target_column = payload.get("target_column")

    if not date_column:
        dates = detect_date_columns(df)
        date_column = dates[0] if dates else None

    if not target_column:
        numeric = [
            c
            for c in df.columns
            if pd.api.types.is_numeric_dtype(df[c])
            and str(c).lower()
            not in {"year", "month"}
        ]

        target_column = (
            numeric[0] if numeric else None
        )

    if not date_column or not target_column:
        raise ValueError(
            "A valid date column and numeric target column are required."
        )

    horizon = int(
        payload.get("horizon", 12)
    )

    horizon = max(
        1,
        min(horizon, 60),
    )

    work = prepare_series(
        df,
        date_column,
        target_column,
    )

    # Preserve the requested external variable for the
    # unified SARIMAX forecasting pipeline.
    if model_name == "unified":
        exog_column = payload.get("exog_column")

        if exog_column:
            column_lookup = {
                str(column).strip().lower(): column
                for column in df.columns
            }

            actual_exog_column = column_lookup.get(
                str(exog_column).strip().lower()
            )

            if actual_exog_column is not None:
                exog_values = pd.to_numeric(
                    df[actual_exog_column],
                    errors="coerce"
                )

                work[actual_exog_column] = (
                    exog_values.ffill().bfill().values
                )

    dates = work[date_column]
    values = work[target_column].astype(float)

    return (
        payload,
        work,
        dates,
        values,
        horizon,
    )


def build_model_response(
    work,
    dates,
    values,
    horizon,
    forecast,
    metadata,
    lower=None,
    upper=None,
):
    future = next_dates(
        dates.iloc[-1],
        horizon,
    )

    forecast_rows = []

    for index in range(horizon):
        row = {
            "date": future[index].strftime(
                "%Y-%m-%d"
            ),
            "value": float(forecast[index]),
        }

        if lower is not None:
            row["lower"] = float(
                lower[index]
            )

        if upper is not None:
            row["upper"] = float(
                upper[index]
            )

        forecast_rows.append(row)

    historical = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "value": float(value),
        }
        for date, value in zip(
            dates,
            values,
        )
    ]

    return {
        "success": True,
        "model": json_safe(metadata),
        "historical": historical,
        "forecast": forecast_rows,
        "parameters": json_safe(
            metadata.get("parameters", {})
        ),
        "aic": metadata.get("aic"),
        "bic": metadata.get("bic"),
    }
# ============================================================
# SPRINT 17.1 - UNIFIED FORECASTING ENDPOINT
# ============================================================

@app.post("/api/forecast/run")
def unified_forecast():
    """
    Unified forecasting endpoint.

    Runs one or more existing forecasting models through a
    single API endpoint without changing the individual
    model implementations.
    """
    try:
        payload, work, dates, values, horizon = model_request("unified")

        requested_models = payload.get("models")

        # If no models are supplied, run all currently supported models.
        if not requested_models:
            requested_models = [
                "tesm",
                "sarima",
                "sarimax",
                "random_forest",
                "xgboost",
                "lstm",
                "gru",
            ]

        # Allow the frontend to request all models explicitly.
        if isinstance(requested_models, str):
            requested_models = [requested_models]

        if "all" in requested_models:
            requested_models = [
                "tesm",
                "sarima",
                "sarimax",
                "random_forest",
                "xgboost",
                "lstm",
                "gru",
            ]

        results = {}
        errors = {}

        for model_name in requested_models:

            model_name = str(model_name).strip().lower()

            try:

                # ------------------------------------------------
                # TESM
                # ------------------------------------------------
                if model_name == "tesm":

                    forecast, metadata = forecast_tesm(
                        values,
                        horizon
                    )
                    lower = None
                    upper = None

                    results[model_name] = build_model_response(
                        work,
                        dates,
                        values,
                        horizon,
                        forecast,
                        metadata,
                        lower,
                        upper
                    )

                # ------------------------------------------------
                # SARIMA
                # ------------------------------------------------
                elif model_name == "sarima":

                    forecast, lower, upper, metadata = forecast_sarima(
                        values,
                        horizon
                    )

                    results[model_name] = build_model_response(
                        work,
                        dates,
                        values,
                        horizon,
                        forecast,
                        metadata,
                        lower,
                        upper
                    )

                # ------------------------------------------------
                # SARIMAX
                # ------------------------------------------------
                elif model_name == "sarimax":

                    exog_column = payload.get("exog_column")

                    if not exog_column:
                        raise ValueError(
                            "exog_column is required for SARIMAX."
                        )

                    # Match the requested column name against the
                    # actual dataset columns, ignoring case and spaces.
                    column_lookup = {
                        str(column).strip().lower(): column
                        for column in work.columns
                    }

                    actual_exog_column = column_lookup.get(
                        str(exog_column).strip().lower()
                    )

                    if actual_exog_column is None:
                        raise ValueError(
                            f"External variable '{exog_column}' "
                            f"was not found in the dataset. "
                            f"Available columns: {list(work.columns)}"
                        )

                    exog = pd.to_numeric(
                        work[actual_exog_column],
                        errors="coerce"
                    ).ffill().bfill()

                    if exog.isna().all():
                        raise ValueError(
                            f"External variable '{actual_exog_column}' "
                            f"contains no usable numeric values."
                        )

                    forecast, lower, upper, metadata = forecast_sarima(
                        values,
                        horizon,
                        exog=exog
                    )

                    metadata["model"] = "SARIMAX"
                    metadata["type"] = "SARIMAX"

                    if "parameters" not in metadata:
                        metadata["parameters"] = {}

                    metadata["parameters"]["exog_column"] = (
                        actual_exog_column
                    )

                    results[model_name] = build_model_response(
                        work,
                        dates,
                        values,
                        horizon,
                        forecast,
                        metadata,
                        lower,
                        upper
                    )



                # ------------------------------------------------
                # RANDOM FOREST
                # ------------------------------------------------
                elif model_name == "random_forest":

                    forecast, metadata = recursive_ml_forecast(
                        values,
                        horizon,
                        "random_forest"
                    )
                    lower=None
                    upper=None

                    # Estimator objects are not JSON serializable.
                    metadata.pop("estimator", None)

                    results[model_name] = build_model_response(
                        work,
                        dates,
                        values,
                        horizon,
                        forecast,
                        metadata,
                        lower,
                        upper
                    )

                # ------------------------------------------------
                # XGBOOST
                # ------------------------------------------------
                elif model_name == "xgboost":

                    forecast, metadata = recursive_ml_forecast(
                        values,
                        horizon,
                        "xgboost"
                    )
                    lower = None
                    upper = None

                    # Estimator objects are not JSON serializable.
                    metadata.pop("estimator", None)

                    results[model_name] = build_model_response(
                        work,
                        dates,
                        values,
                        horizon,
                        forecast,
                        metadata,
                        lower,
                        upper
                    )

                # ------------------------------------------------
                # LSTM
                # ------------------------------------------------
                elif model_name == "lstm":

                    forecast, metadata = forecast_deep_learning(
                        values,
                        horizon,
                        "lstm"
                    )
                    lower = None
                    upper = None

                    metadata.pop(
                        "model",
                        None,
                    )

                    results[model_name] = build_model_response(
                        work,
                        dates,
                        values,
                        horizon,
                        forecast,
                        metadata,
                        lower,
                        upper
                    )

                # ------------------------------------------------
                # GRU
                # ------------------------------------------------
                elif model_name == "gru":

                    forecast, metadata = forecast_deep_learning(
                        values,
                        horizon,
                        "gru"
                    )
                    lower = None
                    upper = None

                    results[model_name] = build_model_response(
                        work,
                        dates,
                        values,
                        horizon,
                        forecast,
                        metadata,
                        lower,
                        upper
                    )

                else:
                    errors[model_name] = (
                        f"Unsupported forecasting model: {model_name}"
                    )

            except Exception as model_error:

                # Keep the unified pipeline running for other models,
                # but print the complete traceback for debugging.
                app.logger.exception(
                    "Unified forecasting failed for model: %s",
                    model_name
                )

                errors[model_name] = str(model_error)
        response = {
            "success": True,
            "dataset_id": payload.get("dataset_id"),
            "requested_models": requested_models,
            "completed_models": list(results.keys()),
            "results": results,
            "errors": errors,
            "horizon": horizon,
        }

        return jsonify(json_safe(response)), 200

    except Exception as exc:

        return error_response(
            f"Unified forecasting failed: {exc}",
            500
        )

@app.post("/api/models/tesm")
@require_auth
@audit_model_run("TESM / Holt-Winters")
def model_tesm():
    try:
        (
            payload,
            work,
            dates,
            values,
            horizon,
        ) = model_request("tesm")

        forecast, metadata = forecast_tesm(
            values,
            horizon,
        )

        return jsonify(
            json_safe(
                build_model_response(
                    work,
                    dates,
                    values,
                    horizon,
                    forecast,
                    metadata,
                )
            )
        )

    except Exception as exc:
        return error_response(
            f"TESM forecast failed: {exc}",
            500,
        )


@app.post("/api/models/sarima")
@require_auth
@audit_model_run("SARIMA")
def model_sarima():
    try:
        (
            payload,
            work,
            dates,
            values,
            horizon,
        ) = model_request("sarima")

        forecast, lower, upper, metadata = (
            forecast_sarima(
                values,
                horizon,
            )
        )

        return jsonify(
            json_safe(
                build_model_response(
                    work,
                    dates,
                    values,
                    horizon,
                    forecast,
                    metadata,
                    lower,
                    upper,
                )
            )
        )

    except Exception as exc:
        return error_response(
            f"SARIMA forecast failed: {exc}",
            500,
        )


@app.post("/api/models/sarimax")
@require_auth
@audit_model_run("SARIMAX")
def model_sarimax():
    try:
        (
            payload,
            work,
            dates,
            values,
            horizon,
        ) = model_request("sarimax")

        exog_column = payload.get(
            "exog_column"
        )

        exog = None

        if (
            exog_column
            and exog_column in work.columns
        ):
            exog = pd.to_numeric(
                work[exog_column],
                errors="coerce",
            ).ffill().bfill()

        forecast, lower, upper, metadata = (
            forecast_sarima(
                values,
                horizon,
                exog=exog,
            )
        )

        metadata["name"] = "SARIMAX"
        metadata["type"] = (
            "SARIMAX(1,1,1)(1,1,1,12)"
        )
        metadata["parameters"]["exog_column"] = (
            exog_column
        )

        return jsonify(
            json_safe(
                build_model_response(
                    work,
                    dates,
                    values,
                    horizon,
                    forecast,
                    metadata,
                    lower,
                    upper,
                )
            )
        )

    except Exception as exc:
        return error_response(
            f"SARIMAX forecast failed: {exc}",
            500,
        )


@app.post("/api/models/random_forest")
@require_auth
@audit_model_run("Random Forest")
def model_random_forest():
    try:
        (
            payload,
            work,
            dates,
            values,
            horizon,
        ) = model_request("random_forest")

        forecast, metadata = (
            recursive_ml_forecast(
                values,
                horizon,
                "random_forest",
            )
        )

        metadata.pop(
            "estimator",
            None,
        )

        return jsonify(
            json_safe(
                build_model_response(
                    work,
                    dates,
                    values,
                    horizon,
                    forecast,
                    metadata,
                )
            )
        )

    except Exception as exc:
        return error_response(
            f"Random Forest forecast failed: {exc}",
            500,
        )


@app.post("/api/models/xgboost")
@require_auth
@audit_model_run("XGBoost")
def model_xgboost():
    try:
        (
            payload,
            work,
            dates,
            values,
            horizon,
        ) = model_request("xgboost")

        forecast, metadata = (
            recursive_ml_forecast(
                values,
                horizon,
                "xgboost",
            )
        )

        metadata.pop(
            "estimator",
            None,
        )

        return jsonify(
            json_safe(
                build_model_response(
                    work,
                    dates,
                    values,
                    horizon,
                    forecast,
                    metadata,
                )
            )
        )

    except Exception as exc:
        return error_response(
            f"XGBoost forecast failed: {exc}",
            500,
        )


@app.post("/api/models/lstm")
@require_auth
@audit_model_run("LSTM")
def model_lstm():
    try:
        (
            payload,
            work,
            dates,
            values,
            horizon,
        ) = model_request("lstm")

        forecast, metadata = (
            forecast_deep_learning(
                values,
                horizon,
                "lstm",
            )
        )

        return jsonify(
            json_safe(
                build_model_response(
                    work,
                    dates,
                    values,
                    horizon,
                    forecast,
                    metadata,
                )
            )
        )

    except Exception as exc:
        return error_response(
            f"LSTM forecast failed: {exc}",
            500,
        )


@app.post("/api/models/gru")
@require_auth
@audit_model_run("GRU")
def model_gru():
    try:
        (
            payload,
            work,
            dates,
            values,
            horizon,
        ) = model_request("gru")

        forecast, metadata = (
            forecast_deep_learning(
                values,
                horizon,
                "gru",
            )
        )

        return jsonify(
            json_safe(
                build_model_response(
                    work,
                    dates,
                    values,
                    horizon,
                    forecast,
                    metadata,
                )
            )
        )

    except Exception as exc:
        return error_response(
            f"GRU forecast failed: {exc}",
            500,
        )


# ============================================================
# VALIDATION
# ============================================================

@app.post("/api/validation")
@require_auth
def validation():
    """
    Run validation against the currently active dataset.

    This route must never return the historical Food Products research
    metrics for an unrelated uploaded dataset. The dataset_id supplied by
    the frontend is resolved, the series is prepared, a chronological
    holdout is created, and every model is fitted on that dataset only.
    """

    def validation_split(values):
        values = (
            pd.Series(values, dtype=float)
            .dropna()
            .reset_index(drop=True)
        )

        if len(values) < 20:
            raise ValueError(
                "At least 20 valid observations are required for validation."
            )

        # Monthly industrial series use a 12-month holdout when possible.
        test_size = (
            12
            if len(values) >= 36
            else max(4, min(12, len(values) // 5))
        )

        # Keep at least 20 observations in the training set.
        if len(values) - test_size < 20:
            test_size = max(4, len(values) - 20)

        if test_size < 1:
            raise ValueError(
                "The active dataset does not contain enough observations "
                "for a validation holdout."
            )

        train = values.iloc[:-test_size].reset_index(drop=True)
        test = values.iloc[-test_size:].reset_index(drop=True)

        return train, test, test_size

    def evaluate_model(model_name, train, test):
        horizon = len(test)

        if model_name == "TESM / Holt-Winters":
            prediction, metadata = forecast_tesm(
                train,
                horizon,
            )
            aic = None

        elif model_name == "SARIMA":
            prediction, _, _, metadata = forecast_sarima(
                train,
                horizon,
            )
            aic = metadata.get("aic")

        elif model_name == "SARIMAX + CPI — Diagnostic":
            # Do not reuse the Food Products CPI series for an arbitrary
            # uploaded dataset. Without an explicitly supplied exogenous
            # series, this is a SARIMAX-form diagnostic with no external
            # regressor.
            prediction, _, _, metadata = forecast_sarima(
                train,
                horizon,
            )
            aic = metadata.get("aic")

        elif model_name == "Random Forest":
            prediction, metadata = recursive_ml_forecast(
                train,
                horizon,
                "random_forest",
            )
            aic = None

        elif model_name == "XGBoost":
            prediction, metadata = recursive_ml_forecast(
                train,
                horizon,
                "xgboost",
            )
            aic = None

        elif model_name == "LSTM":
            prediction, metadata = forecast_deep_learning(
                train,
                horizon,
                "lstm",
            )
            aic = None

        elif model_name == "GRU":
            prediction, metadata = forecast_deep_learning(
                train,
                horizon,
                "gru",
            )
            aic = None

        else:
            raise ValueError(
                f"Unsupported validation model: {model_name}"
            )

        metrics = metric_values(
            test.to_numpy(dtype=float),
            np.asarray(prediction, dtype=float),
        )

        return {
            "model": model_name,
            "mae": metrics["mae"],
            "rmse": metrics["rmse"],
            "mape": metrics["mape"],
            "smape": metrics["smape"],
            "aic": aic,
            "status": "COMPLETED",
        }

    try:
        payload = request.get_json(
            silent=True
        ) or {}

        dataset_id = payload.get("dataset_id")

        if not dataset_id:
            return error_response(
                "Dataset ID is required. Upload a dataset before running validation."
            )

        path = resolve_dataset(dataset_id)

        if path is None:
            return error_response(
                "The active dataset could not be found. Please upload the dataset again."
            )

        df = read_dataset(path)

        if df.empty:
            return error_response(
                "The active dataset is empty."
            )

        date_column = payload.get("date_column")
        target_column = payload.get("target_column")

        if (
            not date_column
            or date_column not in df.columns
        ):
            candidates = detect_date_columns(df)
            date_column = (
                candidates[0]
                if candidates
                else None
            )

        if (
            not target_column
            or target_column not in df.columns
        ):
            numeric_columns = [
                column
                for column in df.columns
                if pd.api.types.is_numeric_dtype(
                    df[column]
                )
                and str(column).strip().lower()
                not in {"year", "month"}
            ]

            preferred_names = {
                "target",
                "index",
                "value",
                "output",
                "production",
                "sales",
                "demand",
                "quantity",
                "amount",
                "revenue",
                "price",
            }

            target_column = next(
                (
                    column
                    for column in numeric_columns
                    if str(column).strip().lower()
                    in preferred_names
                ),
                None,
            )

            if target_column is None and numeric_columns:
                target_column = numeric_columns[0]

        if not date_column:
            return error_response(
                "A valid date column could not be detected for validation."
            )

        if not target_column:
            return error_response(
                "A valid numeric target column could not be detected for validation."
            )

        work = prepare_series(
            df,
            date_column,
            target_column,
        )

        dates = work[date_column].reset_index(drop=True)
        values = (
            work[target_column]
            .astype(float)
            .reset_index(drop=True)
        )

        train, test, test_size = validation_split(
            values
        )

        model_names = [
            "TESM / Holt-Winters",
            "SARIMA",
            "SARIMAX + CPI — Diagnostic",
            "Random Forest",
            "XGBoost",
            "LSTM",
            "GRU",
        ]

        results = []

        for model_name in model_names:
            try:
                results.append(
                    evaluate_model(
                        model_name,
                        train,
                        test,
                    )
                )
            except Exception as exc:
                # One unavailable model must not invalidate the other
                # dataset-specific validation results.
                results.append(
                    {
                        "model": model_name,
                        "mae": None,
                        "rmse": None,
                        "mape": None,
                        "smape": None,
                        "aic": None,
                        "status": "NOT_AVAILABLE",
                        "error": str(exc),
                    }
                )

        test_start = dates.iloc[-test_size].strftime(
            "%Y-%m-%d"
        )
        test_end = dates.iloc[-1].strftime(
            "%Y-%m-%d"
        )
        train_start = dates.iloc[0].strftime(
            "%Y-%m-%d"
        )
        train_end = dates.iloc[-test_size - 1].strftime(
            "%Y-%m-%d"
        )

        dataset_profile = profile_dataset(df)

        methodology = {
            "validation": (
                "Dataset-specific chronological holdout backtest"
            ),
            "frequency": (
                dataset_profile.get("frequency")
                or "Detected from uploaded data"
            ),
            "horizon": int(test_size),
            "training_period": (
                f"{train_start} – {train_end}"
            ),
            "test_period": (
                f"{test_start} – {test_end}"
            ),
            "shuffle": False,
            "notes": [
                "All validation metrics are recalculated from the currently active dataset.",
                "The chronological holdout is excluded from model fitting.",
                "Lower MAE, RMSE and MAPE indicate lower error within this evaluated dataset and holdout period.",
                "AIC applies to likelihood-based statistical models.",
                "The SARIMAX + CPI diagnostic does not reuse the research CPI series for arbitrary uploaded datasets.",
                "Results are dataset-specific and are not universal performance guarantees.",
            ],
        }

        # The frontend already expects both arrays. Keep the contract stable,
        # but make both sections point to the current dataset's calculated
        # evidence instead of the previous hard-coded Food Products metrics.
        successful_results = [
            item
            for item in results
            if item.get("status") == "COMPLETED"
        ]

        log_activity(
            session.get("user_id"),
            "VALIDATION_RUN",
            resource_type="dataset",
            resource_id=dataset_id,
            details={
                "filename": path.name,
                "date_column": date_column,
                "target_column": target_column,
                "observations": int(len(values)),
                "test_horizon": int(test_size),
                "completed_models": [
                    item["model"]
                    for item in successful_results
                ],
            },
        )

        return jsonify(
            json_safe(
                {
                    "success": True,
                    "dataset": {
                        "dataset_id": str(dataset_id),
                        "filename": path.name,
                        "date_column": str(date_column),
                        "target_column": str(target_column),
                        "observations": int(len(values)),
                        "train_observations": int(len(train)),
                        "test_observations": int(len(test)),
                    },
                    "methodology": methodology,
                    "walk_forward": successful_results,
                    "final_test": results,
                }
            )
        )

    except ValueError as exc:
        return error_response(
            f"Validation input error: {exc}",
            400,
        )
    except Exception as exc:
        app.logger.exception(
            "Dataset-specific validation failed"
        )
        return error_response(
            f"Validation failed: {exc}",
            500,
        )


# ============================================================
# EXPLAINABILITY
# ============================================================

def _feature_attribution_from_perturbation(values, model_key, exog=None):
    """Model-agnostic lag attribution for statistical time-series models.

    Each of the most recent 12 observations is perturbed slightly and the
    change in the next-step forecast is measured. This exposes the lagged
    inputs that the fitted statistical model is responding to.
    """
    values = np.asarray(values, dtype=float)
    if len(values) < 30:
        raise ValueError("At least 30 observations are required for attribution.")

    baseline_exog = None
    if exog is not None:
        baseline_exog = pd.Series(exog, dtype=float).reset_index(drop=True)
        if len(baseline_exog) != len(values):
            baseline_exog = None

    if model_key == "tesm":
        baseline, _ = forecast_tesm(values, 1)
        baseline_value = float(baseline[0])
        refit = lambda series: float(forecast_tesm(series, 1)[0][0])
    elif model_key == "sarima":
        baseline, _, _, _ = forecast_sarima(pd.Series(values), 1)
        baseline_value = float(baseline[0])
        refit = lambda series: float(forecast_sarima(pd.Series(series), 1)[0][0])
    elif model_key == "sarimax":
        baseline, _, _, _ = forecast_sarima(
            pd.Series(values), 1, exog=baseline_exog
        )
        baseline_value = float(baseline[0])

        def refit(series):
            return float(
                forecast_sarima(pd.Series(series), 1, exog=baseline_exog)[0][0]
            )
    else:
        raise ValueError(f"Unsupported statistical attribution model: {model_key}")

    scale = float(np.nanstd(values))
    if not np.isfinite(scale) or scale <= 0:
        scale = max(float(np.nanmean(np.abs(values))) * 0.01, 1.0)
    delta = max(scale * 0.05, 1e-6)

    rows = []
    # Use the most recent 12 observations so the labels correspond directly
    # to the forecasting information set: lag_1 is the latest observation.
    for lag in range(1, min(12, len(values) - 1) + 1):
        perturbed = values.copy()
        perturbed[-lag] += delta
        changed = refit(perturbed)
        attribution = abs(changed - baseline_value)
        rows.append({
            "feature": f"lag_{lag}",
            "importance": float(attribution),
            "feature_type": "historical lag",
            "lag": lag,
            "direction": "positive" if changed >= baseline_value else "negative",
        })

    rows.sort(key=lambda item: abs(item["importance"]), reverse=True)
    return rows, "Lag perturbation attribution"


def _deep_learning_feature_attribution(values, model_type):
    """Dataset-specific attribution for LSTM/GRU input lags.

    A model is trained with the same architecture used by forecasting. Each
    input lag is then perturbed and the resulting one-step prediction change
    is measured. This provides an interpretable lag attribution without
    pretending that SHAP for tree models applies to neural networks.
    """
    try:
        tf = importlib.import_module("tensorflow")
        keras = tf.keras
        Sequential = keras.Sequential
        EarlyStopping = keras.callbacks.EarlyStopping
        Input = keras.layers.Input
        LSTM = keras.layers.LSTM
        GRU = keras.layers.GRU
        Dense = keras.layers.Dense
        Dropout = keras.layers.Dropout
    except (ImportError, AttributeError) as exc:
        raise RuntimeError("TensorFlow is not available in the active Python environment.") from exc

    tf.random.set_seed(42)
    np.random.seed(42)
    values = np.asarray(values, dtype=float)
    sequence_length = 12

    if len(values) <= sequence_length + 5:
        raise ValueError("At least 18 observations are required for LSTM/GRU attribution.")

    minimum = float(values.min())
    maximum = float(values.max())
    scale = maximum - minimum
    if scale == 0:
        scale = 1.0
    scaled = (values - minimum) / scale

    X = []
    y = []
    for i in range(sequence_length, len(scaled)):
        X.append(scaled[i-sequence_length:i])
        y.append(scaled[i])
    X = np.asarray(X).reshape(-1, sequence_length, 1)
    y = np.asarray(y)

    model = Sequential([
        Input(shape=(sequence_length, 1)),
        (LSTM(64, return_sequences=True) if model_type == "lstm" else GRU(64, return_sequences=True)),
        Dropout(0.2),
        (LSTM(32) if model_type == "lstm" else GRU(32)),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    callback = EarlyStopping(monitor="loss", patience=12, restore_best_weights=True)
    model.fit(X, y, epochs=80, batch_size=8, shuffle=False, verbose=0, callbacks=[callback])

    latest = scaled[-sequence_length:].copy().reshape(1, sequence_length, 1)
    baseline = float(model.predict(latest, verbose=0)[0][0])
    perturbation = max(float(np.nanstd(scaled)) * 0.05, 1e-4)
    rows = []

    for position in range(sequence_length):
        perturbed = latest.copy()
        perturbed[0, position, 0] += perturbation
        changed = float(model.predict(perturbed, verbose=0)[0][0])
        lag = sequence_length - position
        rows.append({
            "feature": f"lag_{lag}",
            "importance": float(abs(changed - baseline) * scale),
            "feature_type": "neural-network input lag",
            "lag": lag,
            "direction": "positive" if changed >= baseline else "negative",
        })

    rows.sort(key=lambda item: abs(item["importance"]), reverse=True)
    return rows, "Input-lag perturbation attribution"


def _tree_feature_attribution(values, model_key):
    """SHAP/native attribution using the exact ML feature construction."""
    _, metadata = recursive_ml_forecast(values, 1, model_key)
    estimator = metadata["estimator"]
    feature_names = list(metadata["feature_names"])
    training_frame = make_ml_features(values).dropna()
    X = training_frame[feature_names]

    feature_importance = []
    method = "Native tree feature importance"
    try:
        shap = importlib.import_module("shap")
        explainer = shap.TreeExplainer(estimator)
        shap_values = explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        shap_array = np.asarray(shap_values)
        if shap_array.ndim == 3:
            shap_array = shap_array[..., 0]
        mean_abs = np.mean(np.abs(shap_array), axis=0)
        if len(mean_abs) == len(feature_names):
            feature_importance = [
                {
                    "feature": str(feature),
                    "importance": float(value),
                    "feature_type": "engineered ML feature",
                }
                for feature, value in zip(feature_names, mean_abs)
            ]
            method = "SHAP feature attribution"
    except Exception as shap_error:
        app.logger.info(
            "SHAP unavailable for %s; using native feature importance: %s",
            model_key,
            shap_error,
        )

    if not feature_importance:
        native_values = np.asarray(getattr(estimator, "feature_importances_", []), dtype=float)
        if len(native_values) != len(feature_names):
            raise RuntimeError("The active tree model did not return feature attribution values.")
        feature_importance = [
            {
                "feature": str(feature),
                "importance": float(value),
                "feature_type": "engineered ML feature",
            }
            for feature, value in zip(feature_names, native_values)
        ]
    feature_importance.sort(key=lambda item: abs(item["importance"]), reverse=True)
    return feature_importance, method


@app.post("/api/explainability")
@require_auth
def explainability():
    """Return dataset-specific feature attribution for every forecasting model.

    Methods are model-appropriate:
      * TESM/SARIMA/SARIMAX: lag perturbation
      * Random Forest/XGBoost: SHAP, with native importance fallback
      * LSTM/GRU: neural-network input-lag perturbation
    """
    try:
        payload = request.get_json(silent=True) or {}
        dataset_id = payload.get("dataset_id")
        model = str(payload.get("model", "random_forest")).strip().lower()
        target_column = str(payload.get("target_column", "index")).strip()

        aliases = {
            "rf": "random_forest",
            "xgb": "xgboost",
            "holt_winters": "tesm",
            "holt-winters": "tesm",
            "exponential_smoothing": "tesm",
            "sarimax_cpi": "sarimax",
        }
        model_key = aliases.get(model, model)
        supported_models = {"tesm", "sarima", "sarimax", "random_forest", "xgboost", "lstm", "gru"}

        if not dataset_id:
            return error_response("Dataset ID is required.")
        if model_key not in supported_models:
            return jsonify({
                "success": True,
                "analysis": {
                    "supported": False,
                    "model": model,
                    "dataset_id": dataset_id,
                    "target_column": target_column,
                    "method": "Model metadata",
                    "feature_importance": [],
                    "message": "Feature attribution is available for TESM, SARIMA, SARIMAX, Random Forest, XGBoost, LSTM and GRU.",
                },
            })

        dataset_path = resolve_dataset(dataset_id)
        if dataset_path is None:
            return error_response("The active dataset could not be found.")

        df = read_dataset(dataset_path)
        if target_column not in df.columns:
            if "index" in df.columns:
                target_column = "index"
            else:
                numeric = [str(c) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                if not numeric:
                    return error_response("No numeric target column is available for explainability.")
                target_column = numeric[0]

        values = pd.to_numeric(df[target_column], errors="coerce").dropna().to_numpy(dtype=float)
        if len(values) < 30:
            return error_response("At least 30 numeric observations are required for explainability.")

        display_names = {
            "tesm": "TESM / Holt-Winters",
            "sarima": "SARIMA",
            "sarimax": "SARIMAX",
            "random_forest": "Random Forest",
            "xgboost": "XGBoost",
            "lstm": "LSTM",
            "gru": "GRU",
        }

        if model_key in {"tesm", "sarima", "sarimax"}:
            exog = None
            exog_column = payload.get("exog_column")
            if model_key == "sarimax" and exog_column and exog_column in df.columns:
                exog = pd.to_numeric(df[exog_column], errors="coerce").ffill().bfill()
            feature_importance, method = _feature_attribution_from_perturbation(values, model_key, exog=exog)
            parameters = {
                "attribution_window": 12,
                "perturbation": "5% of target standard deviation",
                "features": "lag_1 through lag_12",
            }
            if model_key == "tesm":
                parameters.update({"trend": "additive", "seasonality": "additive", "seasonal_periods": 12})
            elif model_key in {"sarima", "sarimax"}:
                parameters.update({"order": [1, 1, 1], "seasonal_order": [1, 1, 1, 12]})
                if model_key == "sarimax":
                    parameters["exog_column"] = exog_column
        elif model_key in {"random_forest", "xgboost"}:
            feature_importance, method = _tree_feature_attribution(values, model_key)
            parameters = {"feature_count": len(feature_importance), "feature_set": list(make_ml_features(values).dropna().columns[1:])}
        else:
            feature_importance, method = _deep_learning_feature_attribution(values, model_key)
            parameters = {
                "sequence_length": 12,
                "units": [64, 32],
                "dropout": 0.2,
                "epochs": 80,
                "batch_size": 8,
                "features": "lag_1 through lag_12",
            }

        artifact_path = EXPLAIN_FOLDER / f"{model_key}_{clean_name(dataset_id)}_feature_importance.csv"
        pd.DataFrame(feature_importance).to_csv(artifact_path, index=False)

        return jsonify(json_safe({
            "success": True,
            "analysis": {
                "supported": True,
                "model": display_names[model_key],
                "model_key": model_key,
                "dataset_id": dataset_id,
                "target_column": target_column,
                "method": method,
                "parameters": parameters,
                "feature_importance": feature_importance,
                "feature_count": len(feature_importance),
                "artifact": artifact_path.name,
                "interpretation_note": "Feature attribution describes model contribution to the forecast under the selected method; it does not establish real-world causality.",
            },
        }))

    except Exception as exc:
        app.logger.exception("Explainability failed")
        return error_response(f"Explainability failed: {exc}", 500)


# ============================================================
# REPORTING
# ============================================================

@app.post("/api/report")
@require_auth
def generate_report():
    try:
        payload = request.get_json(
            silent=True
        ) or {}

        current_user = get_current_user_record()
        generated_at = datetime.now().isoformat()
        report_id = uuid.uuid4().hex
        dataset_payload = payload.get("dataset", {}) or {}
        data_quality_payload = payload.get("data_quality", {}) or {}
        exploration_payload = payload.get("exploration") or {}
        anomalies_payload = payload.get("anomalies") or {}
        validation_payload = payload.get("validation") or {}
        forecast_payload = payload.get("forecast") or {}
        explainability_payload = payload.get("explainability") or {}

        # Build the executive summary from the CURRENT report payload.
        # Do not preserve generic frontend placeholder text, because the
        # report must describe the dataset that was actually analysed.
        validation_rows = []
        if isinstance(validation_payload, dict):
            validation_rows = (
                validation_payload.get("final_test")
                or validation_payload.get("walk_forward")
                or []
            )
        completed_validation = [
            row for row in validation_rows
            if isinstance(row, dict)
            and row.get("status") == "COMPLETED"
            and row.get("rmse") is not None
        ]
        lowest_rmse_model = None
        if completed_validation:
            lowest_rmse_model = min(
                completed_validation,
                key=lambda row: float(row.get("rmse"))
            )

        rows = dataset_payload.get("rows")
        filename = dataset_payload.get("filename", "the uploaded dataset")
        date_range = dataset_payload.get("date_range")
        anomalies_count = anomalies_payload.get("total")
        if anomalies_count is None:
            anomaly_items = anomalies_payload.get("anomalies")
            if isinstance(anomaly_items, list):
                anomalies_count = len(anomaly_items)

        summary_parts = []
        if rows is not None and date_range:
            summary_parts.append(
                f"The analysis covers {rows} observations from {date_range} in {filename}."
            )
        elif rows is not None:
            summary_parts.append(
                f"The analysis covers {rows} observations in {filename}."
            )
        else:
            summary_parts.append(
                f"The analysis was performed on {filename}."
            )

        quality_status = data_quality_payload.get("quality_status")
        missing_cells = data_quality_payload.get("missing_cells")
        if quality_status:
            quality_sentence = f"Data quality status is {quality_status}."
            if missing_cells is not None:
                quality_sentence += f" The dataset contains {missing_cells} missing cell(s)."
            summary_parts.append(quality_sentence)

        if anomalies_count is not None:
            summary_parts.append(
                f"The analysis identified {anomalies_count} anomaly/anomalies."
            )

        if lowest_rmse_model:
            model_name = lowest_rmse_model.get("model", "the lowest-error model")
            rmse = float(lowest_rmse_model.get("rmse"))
            mape = lowest_rmse_model.get("mape")
            model_sentence = (
                f"Within the evaluated holdout, {model_name} produced the lowest RMSE "
                f"among completed models ({rmse:.3f})."
            )
            if mape is not None:
                model_sentence += f" Its MAPE was {float(mape):.3f}%."
            summary_parts.append(model_sentence)

        forecast_items = forecast_payload.get("forecast") if isinstance(forecast_payload, dict) else None
        if isinstance(forecast_items, list) and forecast_items:
            first_date = forecast_items[0].get("date")
            last_date = forecast_items[-1].get("date")
            summary_parts.append(
                f"A {len(forecast_items)}-period forecast was generated for {first_date} through {last_date}."
            )

        executive_summary = {
            "purpose": " ".join(summary_parts),
            "interpretation": (
                "Forecast values are planning signals. They should be considered together "
                "with dataset-specific validation results, uncertainty information when available, "
                "data quality, anomalies, and relevant operational context. Validation metrics "
                "describe the evaluated dataset and holdout period and should not be treated as "
                "universal performance guarantees."
            ),
        }

        report = {
            "generated_at": generated_at,
            "application": "ForecastIQ",
            "report_type": "Business Forecasting Report",
            "report_id": report_id,
            "prepared_by": {
                "name": current_user.get("name", "") if current_user else "",
                "email": current_user.get("email", "") if current_user else "",
                "role": current_user.get("role", "user") if current_user else "user",
            },
            "administrative_review": {
                "status": "Pending administrative review",
                "note": "This report is an analytical planning document. Final business decisions remain with authorized management.",
            },
            "executive_summary": executive_summary,
            "dataset": dataset_payload,
            "data_quality": data_quality_payload,
            "exploration": exploration_payload,
            "anomalies": anomalies_payload,
            "validation": validation_payload,
            "forecast": forecast_payload,
            "explainability": explainability_payload,
            "governance": {
                "decision_authority": "Authorized business management",
                "analytical_role": "ForecastIQ provides analytical evidence and planning support; it does not independently approve or commit business actions.",
                "review_expectations": [
                    "Review data quality and coverage.",
                    "Review historical validation performance.",
                    "Consider prediction intervals and unusual periods.",
                    "Confirm assumptions with relevant operational stakeholders.",
                    "Document material decisions and assumptions outside the model output where required.",
                ],
            },
        }

        json_path = (
            REPORT_FOLDER
            / f"forecastiq_report_{report_id}.json"
        )

        json_path.write_text(
            json.dumps(
                json_safe(report),
                indent=2,
            ),
            encoding="utf-8",
        )

        excel_path = (
            REPORT_FOLDER
            / f"forecastiq_report_{report_id}.xlsx"
        )

        excel_created = False

        try:
            openpyxl = importlib.import_module("openpyxl")
            Workbook = openpyxl.Workbook
            Font = openpyxl.styles.Font
            PatternFill = openpyxl.styles.PatternFill

            workbook = Workbook()
            summary_sheet = workbook.active
            summary_sheet.title = "Summary"

            dataset = report.get("dataset") or {}

            summary_rows = [
                ["ForecastIQ Business Report", ""],
                ["Generated At", report["generated_at"]],
                ["Application", report["application"]],
                ["Report Type", report["report_type"]],
                ["Dataset", dataset.get("filename", "")],
                ["Rows", dataset.get("rows", "")],
                ["Columns", dataset.get("columns", "")],
                ["Date Column", dataset.get("date_column", "")],
                ["Target Column", dataset.get("target_column", "")],
            ]

            for row in summary_rows:
                summary_sheet.append(row)

            summary_sheet["A1"].font = Font(bold=True, size=16)
            summary_sheet["A1"].fill = PatternFill(
                "solid",
                fgColor="EDE9FE",
            )

            forecast_sheet = workbook.create_sheet("Forecast")
            forecast_sheet.append(
                ["Date", "Forecast", "Lower", "Upper"]
            )

            forecast_data = (
                (report.get("forecast") or {}).get(
                    "forecast",
                    [],
                )
            )

            for item in forecast_data:
                forecast_sheet.append(
                    [
                        item.get("date"),
                        item.get("value"),
                        item.get("lower"),
                        item.get("upper"),
                    ]
                )

            for cell in forecast_sheet[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    "solid",
                    fgColor="EDE9FE",
                )

            validation_sheet = workbook.create_sheet("Validation")
            validation_sheet.append(["Metric", "Value"])

            validation = report.get("validation") or {}
            if isinstance(validation, dict):
                for key, value in validation.items():
                    if isinstance(
                        value,
                        (str, int, float, bool),
                    ):
                        validation_sheet.append(
                            [str(key), value]
                        )

            workbook.save(excel_path)
            excel_created = True

        except Exception as excel_error:
            print("Excel generation warning:", excel_error)

        pdf_path = (
            REPORT_FOLDER
            / f"forecastiq_report_{report_id}.pdf"
        )

        pdf_created = False

        try:
            reportlab_pagesizes = importlib.import_module(
                "reportlab.lib.pagesizes"
            )
            reportlab_styles = importlib.import_module(
                "reportlab.lib.styles"
            )
            reportlab_platypus = importlib.import_module(
                "reportlab.platypus"
            )
            reportlab_colors = importlib.import_module(
                "reportlab.lib.colors"
            )

            A4 = reportlab_pagesizes.A4
            getSampleStyleSheet = (
                reportlab_styles.getSampleStyleSheet
            )
            SimpleDocTemplate = reportlab_platypus.SimpleDocTemplate
            Paragraph = reportlab_platypus.Paragraph
            Spacer = reportlab_platypus.Spacer
            Table = reportlab_platypus.Table
            TableStyle = reportlab_platypus.TableStyle
            colors = reportlab_colors

            document = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36,
            )

            styles = getSampleStyleSheet()
            story = []

            styles = getSampleStyleSheet()
            styles["Title"].fontName = "Helvetica-Bold"
            styles["Title"].fontSize = 20
            styles["Heading2"].fontName = "Helvetica-Bold"
            styles["Heading2"].fontSize = 12
            styles["BodyText"].fontSize = 8.5
            styles["BodyText"].leading = 12
            story = []

            prepared_by = report.get("prepared_by") or {}
            review = report.get("administrative_review") or {}
            governance = report.get("governance") or {}
            executive = report.get("executive_summary") or {}
            dataset = report.get("dataset") or {}
            quality = report.get("data_quality") or {}
            exploration = report.get("exploration") or {}
            anomalies = report.get("anomalies") or {}
            validation = report.get("validation") or {}
            forecast = report.get("forecast") or {}

            story.append(Paragraph("ForecastIQ", styles["Title"]))
            story.append(Paragraph("Business Forecasting Report", styles["Heading2"]))
            story.append(Paragraph(
                "Management Review Copy &middot; Analytical planning document",
                styles["BodyText"],
            ))
            story.append(Spacer(1, 8))

            identity_table = Table(
                [
                    ["Report ID", str(report.get("report_id", "—"))],
                    ["Generated", str(report.get("generated_at", "—"))],
                    ["Prepared by", f"{prepared_by.get('name', '—')} ({prepared_by.get('role', 'user')})"],
                    ["Review status", str(review.get("status", "Pending administrative review"))],
                ],
                colWidths=[105, 365],
            )
            identity_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(identity_table)
            story.append(Spacer(1, 12))

            story.append(Paragraph("Executive Summary", styles["Heading2"]))
            story.append(Paragraph(
                str(executive.get("purpose", "This report provides a factual summary of the forecasting analysis for management review.")),
                styles["BodyText"],
            ))
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                str(executive.get("interpretation", "Forecast values should be interpreted with validation results, uncertainty, data quality, anomalies, and operational context.")),
                styles["BodyText"],
            ))
            story.append(Spacer(1, 12))

            story.append(Paragraph("1. Dataset and Data Quality", styles["Heading2"]))
            dataset_table = Table([
                ["Dataset", dataset.get("filename", "—")],
                ["Observations", str(dataset.get("rows", "—"))],
                ["Columns", str(dataset.get("columns", "—"))],
                ["Date field", dataset.get("date_column", "—")],
                ["Target field", dataset.get("target_column", "—")],
                ["Date range", dataset.get("date_range", "—")],
                ["Quality status", quality.get("quality_status", "Not specified")],
                ["Missing cells", str(quality.get("missing_cells", "—"))],
                ["Duplicate rows", str(quality.get("duplicate_rows", "—"))],
            ], colWidths=[120, 350])
            dataset_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(dataset_table)
            quality_issues = quality.get("quality_issues") or []
            if quality_issues:
                story.append(Spacer(1, 5))
                story.append(Paragraph(
                    "Data-quality observations: " + "; ".join(str(x) for x in quality_issues),
                    styles["BodyText"],
                ))
            story.append(Spacer(1, 12))

            story.append(Paragraph("2. Analytical Observations", styles["Heading2"]))
            observation_rows = [
                ["Historical observations", str(exploration.get("observations", "—"))],
                ["Historical period", f"{exploration.get('first_date', '—')} to {exploration.get('last_date', '—')}"],
                ["Trend description", str(exploration.get("trend", "—"))],
                ["Stationarity", str(exploration.get("stationary", "—"))],
                ["Detected anomalies", str((anomalies.get("summary") or {}).get("total_anomalies", anomalies.get("timeline_count", "—")))],
            ]
            obs_table = Table(observation_rows, colWidths=[160, 310])
            obs_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            story.append(obs_table)
            story.append(Spacer(1, 12))

            story.append(Paragraph("3. Historical Validation", styles["Heading2"]))
            validation_rows = [["Model", "MAE", "RMSE", "MAPE"]]
            for item in (validation.get("final_test") or [])[:12]:
                validation_rows.append([
                    str(item.get("model", "—")),
                    f"{float(item.get('mae', 0)):.3f}" if item.get("mae") is not None else "—",
                    f"{float(item.get('rmse', 0)):.3f}" if item.get("rmse") is not None else "—",
                    f"{float(item.get('mape', 0)):.3f}%" if item.get("mape") is not None else "—",
                ])
            if len(validation_rows) == 1:
                validation_rows.append(["No validation results supplied", "—", "—", "—"])
            validation_table = Table(validation_rows, colWidths=[220, 80, 80, 90], repeatRows=1)
            validation_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(validation_table)
            story.append(Spacer(1, 5))
            story.append(Paragraph(
                "Validation metrics are presented for comparison within the evaluated dataset and period. They should not be interpreted as universal performance guarantees.",
                styles["BodyText"],
            ))
            story.append(Spacer(1, 12))

            story.append(Paragraph("4. Forecast and Uncertainty", styles["Heading2"]))
            forecast_rows = [["Period", "Forecast", "Lower", "Upper"]]
            for item in (forecast.get("forecast") or [])[:24]:
                forecast_rows.append([
                    str(item.get("date", "—")),
                    f"{float(item.get('value', 0)):.2f}" if item.get("value") is not None else "—",
                    f"{float(item.get('lower')):.2f}" if item.get("lower") is not None else "—",
                    f"{float(item.get('upper')):.2f}" if item.get("upper") is not None else "—",
                ])
            if len(forecast_rows) == 1:
                forecast_rows.append(["No forecast supplied", "—", "—", "—"])
            forecast_table = Table(forecast_rows, colWidths=[125, 105, 105, 105], repeatRows=1)
            forecast_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ]))
            story.append(forecast_table)
            story.append(Spacer(1, 12))

            story.append(Paragraph("5. Management Considerations", styles["Heading2"]))
            management_points = [
                "Consider the forecast as an analytical planning input rather than a standalone commitment or approval.",
                "Review prediction intervals when assessing the range of plausible outcomes.",
                "Review detected anomalies and structural changes before relying on historical patterns for future planning.",
                "Where material operational, financial, or supply-chain decisions are involved, confirm assumptions with the responsible business team.",
                "Retain the report and supporting analysis when an auditable record of the planning decision is required.",
            ]
            for point in management_points:
                story.append(Paragraph("&bull; " + point, styles["BodyText"]))
                story.append(Spacer(1, 2))
            story.append(Spacer(1, 8))

            story.append(Paragraph("6. Governance and Administrative Review", styles["Heading2"]))
            story.append(Paragraph(
                str(review.get("note", "This report is an analytical planning document. Final business decisions remain with authorized management.")),
                styles["BodyText"],
            ))
            story.append(Spacer(1, 5))
            story.append(Paragraph(
                str(governance.get("analytical_role", "ForecastIQ provides analytical evidence and planning support; it does not independently approve or commit business actions.")),
                styles["BodyText"],
            ))
            story.append(Spacer(1, 5))
            story.append(Paragraph(
                "Administrative review status: " + str(review.get("status", "Pending administrative review")),
                styles["BodyText"],
            ))
            story.append(Spacer(1, 5))
            story.append(Paragraph(
                "Administrative controls include account oversight, audit review, report ownership visibility, and system-status review. Passwords and password hashes are not included in administrative report data.",
                styles["BodyText"],
            ))

            document.build(story)
            pdf_created = True

        except Exception as pdf_error:
            print(
                "PDF generation warning:",
                pdf_error,
            )

        # Persist report ownership and review metadata for administrative oversight.
        if current_user is not None:
            report_history_collection.insert_one(
                {
                    "report_id": report_id,
                    "user_id": current_user["_id"],
                    "dataset_id": dataset_payload.get("dataset_id"),
                    "dataset_filename": dataset_payload.get("filename"),
                    "created_at": generated_at,
                    "review_status": "Pending administrative review",
                    "files": {
                        "json": str(json_path.relative_to(BASE_DIR)),
                        "excel": str(excel_path.relative_to(BASE_DIR)) if excel_created else None,
                        "pdf": str(pdf_path.relative_to(BASE_DIR)) if pdf_created else None,
                    },
                }
            )
            log_activity(
                current_user["_id"],
                "REPORT_GENERATED",
                "report",
                report_id,
                {"dataset_id": dataset_payload.get("dataset_id")},
            )

        return jsonify(
            {
                "success": True,
                "report": {
                    "report_id": report_id,
                    "json_file": str(
                        json_path.relative_to(
                            BASE_DIR
                        )
                    ),
                    "excel_available": excel_created,
                    "excel_file": (
                        str(
                            excel_path.relative_to(BASE_DIR)
                        )
                        if excel_created
                        else None
                    ),
                    "download_excel": (
                        f"/api/reports/{report_id}/excel"
                        if excel_created
                        else None
                    ),
                    "pdf_available": pdf_created,
                    "pdf_file": (
                        str(
                            pdf_path.relative_to(
                                BASE_DIR
                            )
                        )
                        if pdf_created
                        else None
                    ),
                    "download_json": (
                        f"/api/reports/{report_id}/json"
                    ),
                    "download_pdf": (
                        f"/api/reports/{report_id}/pdf"
                        if pdf_created
                        else None
                    ),
                },
            }
        )

    except Exception as exc:
        return error_response(
            f"Report generation failed: {exc}",
            500,
        )


@app.get("/api/reports/<report_id>/json")
@require_auth
@audit_report_download("JSON")
def download_report_json(report_id):
    path = (
        REPORT_FOLDER
        / f"forecastiq_report_{clean_name(report_id)}.json"
    )

    if not path.exists():
        return error_response(
            "Report was not found.",
            404,
        )

    return send_file(
        path,
        as_attachment=True,
        download_name=path.name,
        mimetype="application/json",
    )


@app.get("/api/reports/<report_id>/excel")
@require_auth
@audit_report_download("Excel")
def download_report_excel(report_id):
    path = (
        REPORT_FOLDER
        / f"forecastiq_report_{clean_name(report_id)}.xlsx"
    )

    if not path.exists():
        return error_response(
            "Excel report was not found. Generate the report first.",
            404,
        )

    return send_file(
        path,
        as_attachment=True,
        download_name=path.name,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


@app.get("/api/reports/<report_id>/pdf")
@require_auth
@audit_report_download("PDF")
def download_report_pdf(report_id):
    path = (
        REPORT_FOLDER
        / f"forecastiq_report_{clean_name(report_id)}.pdf"
    )

    if not path.exists():
        return error_response(
            "PDF report was not found. Generate the report first.",
            404,
        )

    return send_file(
        path,
        as_attachment=True,
        download_name=path.name,
        mimetype="application/pdf",
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(413)
def too_large(_error):
    return error_response(
        "The uploaded file is too large. Maximum size is 100 MB.",
        413,
    )


@app.errorhandler(404)
def not_found(_error):
    return jsonify(
        {
            "success": False,
            "error": "API route not found.",
        }
    ), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify(
        {
            "success": False,
            "error": "Internal server error.",
        }
    ), 500


if __name__ == "__main__":
    print("=" * 60)
    print("ForecastIQ API")
    print("http://127.0.0.1:5000")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
