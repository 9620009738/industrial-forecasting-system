import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LineChart as RechartsLineChart,
  BarChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  Activity,
  Shield,
  Users,
  UserCog,
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Database,
  FileSpreadsheet,
  FileText,
  Gauge,
  Info,
  LockKeyhole,
  Mail,
  UserRound,
  Eye,
  EyeOff,
  LogOut,
  LineChart,
  Loader2,
  Menu,
  RefreshCcw,
  Settings2,
  ShieldCheck,
  Sparkles,
  Table2,
  Trash2,
  Upload,
  X,
} from "lucide-react";

/* ============================================================
   NAVIGATION
============================================================ */

const navigation = [
  { label: "DATA", title: "Dataset", icon: Database },
  { label: "PROFILE", title: "Data Quality", icon: BarChart3 },
  { label: "CLEAN", title: "Prepare", icon: Settings2 },
  { label: "EXPLORE", title: "Trends", icon: LineChart },
  { label: "ANOMALIES", title: "Anomalies", icon: AlertTriangle },
  { label: "MODELS", title: "Forecasting Models", icon: BrainCircuit },
  { label: "VALIDATE", title: "Model Validation", icon: Gauge },
  { label: "FORECAST", title: "Business Forecast", icon: Activity },
  { label: "EXPLAIN", title: "Why This Forecast?", icon: Sparkles },
  { label: "REPORT", title: "Reports", icon: FileText },
  { label: "ADMIN", title: "Administration", icon: Shield },
];

/* ============================================================
   WORKFLOW
============================================================ */

const workflow = [
  ["01", "DATA", "Upload business data"],
  ["02", "PROFILE", "Check data quality"],
  ["03", "CLEAN", "Prepare forecasting data"],
  ["04", "EXPLORE", "Understand trends"],
  ["05", "ANOMALIES", "Find unusual activity"],
  ["06", "MODELS", "Compare forecasting methods"],
  ["07", "VALIDATE", "Test historical accuracy"],
  ["08", "FORECAST", "Plan ahead with predictions"],
  ["09", "EXPLAIN", "Understand forecast drivers"],
  ["10", "REPORT", "Share business insights"],
];

/* ============================================================
   MODELS
============================================================ */

const models = [
  "TESM / Holt-Winters",
  "SARIMA",
  "SARIMAX",
  "Random Forest",
  "XGBoost",
  "LSTM",
  "GRU",
];

/* ============================================================
   DEMO DATASET
============================================================ */

const demoRows = [
  {
    date: "2024-04-01",
    index: 119.8,
    growth_rate: 4.2,
    month: 4,
  },
  {
    date: "2024-05-01",
    index: 116.4,
    growth_rate: -2.8,
    month: 5,
  },
  {
    date: "2024-06-01",
    index: 118.3,
    growth_rate: 1.6,
    month: 6,
  },
  {
    date: "2024-07-01",
    index: 119.9,
    growth_rate: 1.4,
    month: 7,
  },
  {
    date: "2024-08-01",
    index: 122.3,
    growth_rate: 2.0,
    month: 8,
  },
];

/* ============================================================
   HELPERS
============================================================ */

function formatBytes(bytes) {
  if (!bytes) return "0 KB";

  const units = ["Bytes", "KB", "MB", "GB"];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));

  return `${(bytes / Math.pow(1024, index)).toFixed(1)} ${units[index]}`;
}

function getFileExtension(filename) {
  return filename.split(".").pop()?.toLowerCase() || "";
}

function isSupportedFile(filename) {
  const extension = getFileExtension(filename);

  return ["csv", "xlsx", "xls"].includes(extension);
}

function ForecastIQLogo({ size = 40 }) {
  return (
    <div
      className="flex shrink-0 items-center justify-center rounded-xl bg-red-600 shadow-lg shadow-red-600/20"
      style={{ width: size, height: size }}
      aria-label="ForecastIQ logo"
      title="ForecastIQ"
    >
      <svg
        viewBox="0 0 40 40"
        className="h-5/6 w-5/6"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M8 27.5L15 20.5L20 24L30.5 12.5"
          stroke="white"
          strokeWidth="3.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M25.5 12.5H30.5V17.5"
          stroke="white"
          strokeWidth="3.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle
          cx="8"
          cy="27.5"
          r="2"
          fill="white"
        />
        <circle
          cx="15"
          cy="20.5"
          r="2"
          fill="white"
        />
        <circle
          cx="20"
          cy="24"
          r="2"
          fill="white"
        />
      </svg>
    </div>
  );
}

/* ============================================================
   APP
============================================================ */

function App() {
  const [activePage, setActivePage] = useState("DATA");

  /* ==========================================================
     AUTHENTICATION
  ========================================================== */

  const [authLoading, setAuthLoading] = useState(true);
  const [authUser, setAuthUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");
  const [authError, setAuthError] = useState("");
  const [authSubmitting, setAuthSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [authForm, setAuthForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [resetCode, setResetCode] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [resetConfirmPassword, setResetConfirmPassword] = useState("");
  const [resetMessage, setResetMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function restoreAuthentication() {
      try {
        const response = await fetch(
          "http://localhost:5000/api/auth/me",
          {
            method: "GET",
            credentials: "include",
          },
        );

        if (!response.ok) {
          if (!cancelled) setAuthUser(null);
          return;
        }

        const result = await response.json();

        if (!cancelled && result.success && result.user) {
          setAuthUser(result.user);
        }
      } catch (error) {
        console.error("Authentication restore error:", error);
        if (!cancelled) setAuthUser(null);
      } finally {
        if (!cancelled) setAuthLoading(false);
      }
    }

    restoreAuthentication();

    return () => {
      cancelled = true;
    };
  }, []);

  function updateAuthField(field, value) {
    setAuthForm((current) => ({
      ...current,
      [field]: value,
    }));
    setAuthError("");
  }

  function switchAuthMode(mode) {
    setAuthMode(mode);
    setAuthError("");
    setResetMessage("");
    setShowPassword(false);
    setShowConfirmPassword(false);
  }

  async function handleForgotPassword(event) {
    event.preventDefault();
    setAuthError("");
    setResetMessage("");

    const email = authForm.email.trim().toLowerCase();
    if (!email) {
      setAuthError("Enter the email address registered with ForecastIQ.");
      return;
    }

    setAuthSubmitting(true);

    try {
      const response = await fetch(
        "http://localhost:5000/api/auth/forgot-password",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ email }),
        },
      );

      const result = await response.json().catch(() => ({}));

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Unable to start password reset.");
      }

      setResetCode(result.dev_reset_code || "");
      setResetMessage(result.message || "Check your email for the reset code.");
      setAuthMode("reset");
    } catch (error) {
      console.error("Forgot password error:", error);
      setAuthError(error.message || "Unable to start password reset.");
    } finally {
      setAuthSubmitting(false);
    }
  }

  async function handleResetPassword(event) {
    event.preventDefault();
    setAuthError("");
    setResetMessage("");

    if (!/^\d{6}$/.test(resetCode.trim())) {
      setAuthError("Enter the 6-digit reset code.");
      return;
    }

    if (resetPassword.length < 8) {
      setAuthError("Password must contain at least 8 characters.");
      return;
    }

    setAuthSubmitting(true);

    try {
      const response = await fetch(
        "http://localhost:5000/api/auth/reset-password",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            email: authForm.email.trim().toLowerCase(),
            code: resetCode.trim(),
            password: resetPassword,
            confirm_password: resetConfirmPassword,
          }),
        },
      );

      const result = await response.json().catch(() => ({}));

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Password reset failed.");
      }

      setResetCode("");
      setResetPassword("");
      setResetConfirmPassword("");
      setAuthForm((current) => ({
        ...current,
        password: "",
        confirmPassword: "",
      }));
      setAuthMode("login");
      showToast("Password reset successfully. Please sign in.");
    } catch (error) {
      console.error("Reset password error:", error);
      setAuthError(error.message || "Password reset failed.");
    } finally {
      setAuthSubmitting(false);
    }
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setAuthError("");
    setAuthSubmitting(true);

    try {
      const endpoint =
        authMode === "register"
          ? "http://localhost:5000/api/auth/register"
          : "http://localhost:5000/api/auth/login";

      const payload =
        authMode === "register"
          ? {
              name: authForm.name.trim(),
              email: authForm.email.trim(),
              password: authForm.password,
              confirm_password: authForm.confirmPassword,
            }
          : {
              email: authForm.email.trim(),
              password: authForm.password,
            };

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok || !result.success) {
        throw new Error(
          result.error ||
            (authMode === "register"
              ? "Registration failed."
              : "Sign in failed."),
        );
      }

      if (authMode === "register") {
        setAuthForm({
          name: "",
          email: authForm.email.trim(),
          password: "",
          confirmPassword: "",
        });
        setAuthMode("login");
        setShowPassword(false);
        setShowConfirmPassword(false);
        showToast("Account created successfully. Please sign in.");
        return;
      }

      setAuthUser(result.user);
      setAuthForm((current) => ({
        ...current,
        password: "",
        confirmPassword: "",
      }));
      showToast(`Welcome back, ${result.user?.name || "User"}.`);
    } catch (error) {
      console.error("Authentication error:", error);
      setAuthError(
        error.message ||
          "Unable to connect to the ForecastIQ authentication service.",
      );
    } finally {
      setAuthSubmitting(false);
    }
  }

  async function handleLogout() {
    try {
      await fetch("http://localhost:5000/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setAuthUser(null);
      setActivePage("DATA");
      setDatasetLoaded(false);
      setSelectedFile(null);
      setDatasetId(null);
      setActiveDatasetId(null);
      setDatasetProfile(null);
      setRows(demoRows);
      showToast("You have been signed out.");
    }
  }

  useEffect(() => {
    document.querySelector("main")?.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }, [activePage]);

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);

  const [datasetId, setDatasetId] = useState(null);

  const [activeDatasetId, setActiveDatasetId] = useState(null);

  const [uploadError, setUploadError] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const [datasetLoaded, setDatasetLoaded] = useState(false);

  const [showDataWorkspace, setShowDataWorkspace] = useState(false);

  const [dateColumn, setDateColumn] = useState("date");

  const [targetColumn, setTargetColumn] = useState("index");

  const [datasetColumns, setDatasetColumns] = useState([
    "date",
    "year",
    "month",
    "index",
    "growth_rate",
  ]);

  const [rows, setRows] = useState(demoRows);

  const [quality, setQuality] = useState({
    rows: 156,
    columns: 5,
    missing: 1,
    duplicates: 0,
    numericColumns: 3,
    dateRange: "Apr 2012 – Mar 2025",
  });
  const [datasetProfile, setDatasetProfile] = useState(null);

  const [cleanConfig, setCleanConfig] = useState({
  missing_method: "none",
  duplicate_method: "keep",
  outlier_method: "none",
  transformation: "none",
});

const [cleaning, setCleaning] = useState(false);
const [cleanResult, setCleanResult] = useState(null);
const [cleanError, setCleanError] = useState("");
const [exploreLoading, setExploreLoading] = useState(false);
const [exploreResult, setExploreResult] = useState(null);
const [exploreError, setExploreError] = useState("");

const [anomalyLoading, setAnomalyLoading] = useState(false);
const [anomalyResult, setAnomalyResult] = useState(null);
const [anomalyError, setAnomalyError] = useState("");
const [modelLoading, setModelLoading] = useState(false);
const [modelResult, setModelResult] = useState(null);
const [unifiedForecastResult, setUnifiedForecastResult] =
  useState(null);
const [modelError, setModelError] = useState("");
const [selectedModel, setSelectedModel] = useState("tesm");
const [forecastHorizon, setForecastHorizon] = useState(12);

const [validationLoading, setValidationLoading] = useState(false);
const [validationResult, setValidationResult] = useState(null);
const [validationError, setValidationError] = useState("");
const [explainLoading, setExplainLoading] = useState(false);
const [explainResult, setExplainResult] = useState(null);
const [explainError, setExplainError] = useState("");
const [reportLoading, setReportLoading] = useState(false);
const [adminLoading, setAdminLoading] = useState(false);
const [adminError, setAdminError] = useState("");
const [adminOverview, setAdminOverview] = useState(null);

const [modelConfig, setModelConfig] = useState({
  exog_column: "",
});

const modelChartData = useMemo(() => {
  if (!modelResult) {
    return [];
  }

  const historical = (modelResult.historical || []).map((item) => ({
    date: item.date,
    actual: Number(item.value),
    forecast: null,
    lower: null,
    upper: null,
  }));

  const forecast = (modelResult.forecast || []).map((item) => ({
    date: item.date,
    actual: null,
    forecast: Number(item.value),
    lower:
      item.lower !== undefined && item.lower !== null
        ? Number(item.lower)
        : null,
    upper:
      item.upper !== undefined && item.upper !== null
        ? Number(item.upper)
        : null,
  }));

  return [...historical, ...forecast];
}, [modelResult]);

const unifiedModelComparison = useMemo(() => {
  const results = unifiedForecastResult?.results;

  if (!results || typeof results !== "object") {
    return [];
  }

  const finalTestRows = Array.isArray(validationResult?.final_test)
    ? validationResult.final_test
    : [];

  const walkForwardRows = Array.isArray(validationResult?.walk_forward)
    ? validationResult.walk_forward
    : [];

  const normalize = (value) =>
    String(value || "")
      .trim()
      .toLowerCase()
      .replace(/[_-]+/g, " ")
      .replace(/\s+/g, " ");

  /*
   * IMPORTANT:
   * The unified forecast API and validation API use slightly
   * different display names. Match by MODEL KEY, not by the
   * complete display name.
   */
  const modelAliases = {
    tesm: [
      "tesm",
      "holt winters",
      "holt winter",
      "tesm / holt winters",
      "holt winters / tesm",
    ],

    sarima: [
      "sarima",
      "sarima paper specification",
      "sarima — paper specification",
      "sarima - paper specification",
    ],

    sarimax: [
      "sarimax",
      "sarimax cpi",
      "sarimax + cpi",
      "sarimax cpi diagnostic",
      "sarimax + cpi diagnostic",
      "sarimax + cpi — diagnostic",
    ],

    random_forest: [
      "random forest",
      "random_forest",
    ],

    xgboost: [
      "xgboost",
      "xg boost",
    ],

    lstm: [
      "lstm",
    ],

    gru: [
      "gru",
    ],
  };

  const matchesModel = (rowModel, modelKey) => {
    const normalizedRow = normalize(rowModel);
    const aliases = modelAliases[modelKey] || [modelKey];

    return aliases.some((alias) => {
      const normalizedAlias = normalize(alias);

      return (
        normalizedRow === normalizedAlias ||
        normalizedRow.includes(normalizedAlias) ||
        normalizedAlias.includes(normalizedRow)
      );
    });
  };

  const findValidationRow = (rows, modelKey) => {
    return (
      rows.find((row) =>
        matchesModel(row?.model, modelKey)
      ) || null
    );
  };

  const numericValue = (value) => {
    const number = Number(value);

    return Number.isFinite(number)
      ? number
      : null;
  };

  return Object.entries(results)
    .map(([modelKey, result]) => {
      if (!result || result.success === false) {
        return null;
      }

      const model = result.model || {};

      const finalTest = findValidationRow(
        finalTestRows,
        modelKey
      );

      const walkForward = findValidationRow(
        walkForwardRows,
        modelKey
      );

      return {
        key: modelKey,

        name:
          model.name ||
          modelKey.replace(/_/g, " "),

        walkForwardMae: numericValue(
          walkForward?.mae
        ),

        walkForwardRmse: numericValue(
          walkForward?.rmse
        ),

        walkForwardMape: numericValue(
          walkForward?.mape
        ),

        finalTestMae: numericValue(
          finalTest?.mae
        ),

        finalTestRmse: numericValue(
          finalTest?.rmse
        ),

        finalTestMape: numericValue(
          finalTest?.mape
        ),

        aic: numericValue(
          model.aic
        ),

        bic: numericValue(
          model.bic
        ),

        forecastCount:
          Array.isArray(result.forecast)
            ? result.forecast.length
            : 0,
      };
    })
    .filter(Boolean);
}, [
  unifiedForecastResult,
  validationResult,
]);

const [toast, setToast] = useState(null);

/* ==========================================================
STATS
========================================================== */

  const stats = useMemo(
    () => [
      {
        label: "DATASETS",
        value: datasetLoaded ? "01" : "00",
        detail: datasetLoaded ? "Dataset loaded" : "No dataset loaded",
        icon: Database,
      },
      {
        label: "MODELS",
        value: "07",
        detail: "Available algorithms",
        icon: BrainCircuit,
      },
      {
        label: "VALIDATION",
        value: "READY",
        detail: "Walk-forward enabled",
        icon: Gauge,
      },
      {
        label: "EXPLAINABILITY",
        value: "SHAP",
        detail: "Feature attribution",
        icon: Sparkles,
      },
    ],
    [datasetLoaded],
  );

  /* ==========================================================
     TOAST
  ========================================================== */

  function showToast(message, type = "success") {
    setToast({ message, type });

    window.setTimeout(() => {
      setToast(null);
    }, 3000);
  }

  /* ==========================================================
     FILE UPLOAD
  ========================================================== */

  async function handleFileChange(event) {
  const file = event.target.files?.[0];

  setUploadError("");

  if (!file) {
    return;
  }

  if (!isSupportedFile(file.name)) {
    setSelectedFile(null);
    setDatasetLoaded(false);
    setUploadError(
      "Unsupported file type. Please select a CSV, XLSX, or XLS file."
    );
    return;
  }

  setIsLoading(true);

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://localhost:5000/api/upload", {
      method: "POST",
        credentials: "include",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(
        result.error || "The backend could not process the dataset."
      );
    }

const dataset = result.dataset;
const profile = dataset.profile;

setDatasetId(dataset.id);
setActiveDatasetId(dataset.id);
setDatasetProfile(profile);

    setSelectedFile({
      name: dataset.filename,
      size: file.size,
      type: file.type,
    });

    setDatasetLoaded(true);

    setDatasetColumns(profile.column_names);

    const detectedDateColumn =
      dataset.date_suggestions?.[0] ||
      profile.column_names.find((column) =>
        column.toLowerCase().includes("date")
      ) ||
      profile.column_names[0];

const numericColumns = profile.numeric_columns || [];
const columnNames = profile.column_names || [];

const preferredTargetNames = [
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
];

const normalizedColumns = columnNames.map((column) => ({
  original: column,
  normalized: String(column).trim().toLowerCase(),
}));

const preferredTargetColumn =
  normalizedColumns.find((column) =>
    preferredTargetNames.includes(column.normalized)
  )?.original;

const detectedTargetColumn =
  preferredTargetColumn ||
  dataset.target_suggestions?.find(
    (column) =>
      numericColumns.includes(column) &&
      column !== detectedDateColumn
  ) ||
  numericColumns.find(
    (column) =>
      column !== detectedDateColumn &&
      !["year", "month"].includes(
        String(column).trim().toLowerCase()
      )
  ) ||
  numericColumns[0] ||
  columnNames[0];

    setDateColumn(detectedDateColumn);
    setTargetColumn(detectedTargetColumn);

    setRows(dataset.preview || []);

    setQuality({
      rows: profile.rows,
      columns: profile.columns,
      missing: profile.missing_cells,
      duplicates: profile.duplicate_rows,
      numericColumns: profile.numeric_columns?.length || 0,
      dateRange: "Detected from dataset",
    });

    setShowDataWorkspace(true);

    showToast(`Dataset uploaded: ${dataset.filename}`);
  } catch (error) {
    console.error("Dataset upload error:", error);

    setSelectedFile(null);
    setDatasetLoaded(false);
    setShowDataWorkspace(false);

    setUploadError(
      error.message ||
        "Unable to connect to the forecasting backend."
    );
  } finally {
    setIsLoading(false);

    // Allow selecting the same file again
    event.target.value = "";
  }
}
async function handleCleanDataset() {
  setCleaning(true);
  setCleanError("");
  setCleanResult(null);

  try {
    if (!datasetId) {
      throw new Error(
        "No uploaded dataset is available. Please upload a dataset first."
      );
    }

    const response = await fetch(
      "http://localhost:5000/api/clean",
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dataset_id: datasetId,
          date_column: dateColumn,
          target_column: targetColumn,
          missing_method: cleanConfig.missing_method,
          duplicate_method: cleanConfig.duplicate_method,
          outlier_method: cleanConfig.outlier_method,
          transformation: cleanConfig.transformation,
        }),
      }
    );

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(
        result.error ||
          "The backend could not clean the dataset."
      );
    }

setCleanResult(result.dataset);

if (result.dataset?.dataset_id) {
  setActiveDatasetId(result.dataset.dataset_id);
}

showToast("Dataset cleaned successfully.");

  } catch (error) {
    console.error("Dataset cleaning error:", error);

    setCleanError(
      error.message ||
        "Unable to clean the dataset."
    );

  } finally {
    setCleaning(false);
  }
}

async function handleExploreDataset() {
  setExploreLoading(true);
  setExploreError("");
  setExploreResult(null);

  try {
    if (!activeDatasetId) {
      throw new Error(
        "No active dataset is available. Please upload and prepare a dataset first."
      );
    }

    const response = await fetch(
      "http://localhost:5000/api/explore",
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dataset_id: activeDatasetId,
          date_column: dateColumn,
          target_column: targetColumn,
        }),
      }
    );

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(
        result.error ||
          "The backend could not analyze the dataset."
      );
    }

    setExploreResult(result.analysis);

    showToast("Exploration analysis completed.");
  } catch (error) {
    console.error("Explore analysis error:", error);

    setExploreError(
      error.message ||
        "Unable to analyze the dataset."
    );
  } finally {
    setExploreLoading(false);
  }
}

/* ==========================================================
ANOMALY ANALYSIS
========================================================== */

async function handleAnomalyAnalysis() {
    const currentDatasetId = activeDatasetId || datasetId;

  if (!datasetLoaded || !currentDatasetId) {
    setAnomalyError(
      "Please upload and configure a dataset before running anomaly analysis."
    );
    showToast(
      "Upload a dataset before running anomaly analysis.",
      "info"
    );
    return;
  }

  setAnomalyLoading(true);
  setAnomalyError("");

  try {
    const response = await fetch(
      "http://localhost:5000/api/anomalies",
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dataset_id: currentDatasetId,
          date_column: dateColumn,
          target_column: targetColumn,
        }),
      }
    );

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(
        result.error ||
          "The backend could not complete anomaly analysis."
      );
    }

    setAnomalyResult(result.analysis);

    showToast("Anomaly analysis completed.");

  } catch (error) {
    console.error(
      "Anomaly analysis error:",
      error
    );

    setAnomalyError(
      error.message ||
        "Unable to load anomaly analysis."
    );

  } finally {
    setAnomalyLoading(false);
  }
}

async function handleUnifiedForecast(modelsToRun = [selectedModel]) {
  const currentDatasetId = activeDatasetId || datasetId;

  if (!currentDatasetId) {
    throw new Error(
      "Please upload a dataset before running a forecasting model."
    );
  }

  const normalizedModels = Array.isArray(modelsToRun)
    ? modelsToRun.filter(Boolean)
    : [modelsToRun].filter(Boolean);

  if (!normalizedModels.length) {
    throw new Error("At least one forecasting model must be selected.");
  }

  const response = await fetch(
    "http://localhost:5000/api/forecast/run",
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        dataset_id: currentDatasetId,
        date_column: dateColumn,
        target_column: targetColumn,
        horizon: Number(forecastHorizon),
        models: normalizedModels,
        exog_column: modelConfig.exog_column || null,
      }),
    }
  );

  const result = await response.json().catch(() => ({}));

  if (!response.ok || !result.success) {
    const backendErrors = result.errors || {};
    const firstError = Object.values(backendErrors)[0];

    throw new Error(
      firstError ||
        result.error ||
        "The unified forecasting service could not complete the forecast."
    );
  }

  return result;
}

async function handleSelectedModelForecast() {
  setModelLoading(true);
  setModelError("");
  setModelResult(null);

  try {
    const result = await handleUnifiedForecast([selectedModel]);
    setUnifiedForecastResult(result);

    const selectedResult = result.results?.[selectedModel];

    if (!selectedResult?.success) {
      throw new Error(
        result.errors?.[selectedModel] ||
          `${getModelDisplayName(selectedModel)} did not return a valid forecast.`
      );
    }

    setModelResult(selectedResult);

    showToast(
      `${getModelDisplayName(selectedModel)} forecast completed successfully.`
    );
  } catch (error) {
    console.error(`${selectedModel} forecast error:`, error);

    setModelError(
      error.message ||
        `Unable to run the ${getModelDisplayName(selectedModel)} model.`
    );
  } finally {
    setModelLoading(false);
  }
}

async function handleAllModelsForecast() {
  setModelLoading(true);
  setModelError("");

  try {
    // SARIMAX is kept out of this batch because the current unified
    // backend contract requires an explicit exogenous column for it.
    const allModels = [
      "tesm",
      "sarima",
      "random_forest",
      "xgboost",
      "lstm",
      "gru",
    ];

    const result = await handleUnifiedForecast(allModels);

    setUnifiedForecastResult(result);

    const successfulModels = Object.entries(result.results || {})
      .filter(([, modelResult]) => modelResult?.success)
      .map(([modelKey]) => modelKey);

    if (!successfulModels.length) {
      throw new Error(
        "The unified forecasting service did not return a successful result for any model."
      );
    }

    showToast(
      `${successfulModels.length} forecasting models completed successfully.`
    );
  } catch (error) {
    console.error("All-model forecast error:", error);

    setModelError(
      error.message ||
        "Unable to run the unified forecast for all models."
    );
  } finally {
    setModelLoading(false);
  }
}

function handleExportForecastCsv() {
  if (!modelResult?.forecast?.length) {
    showToast("Run a forecast before exporting.", "info");
    return;
  }

  const rows = modelResult.forecast.map((item) => ({
    date: item.date,
    forecast: item.value,
    lower: item.lower ?? "",
    upper: item.upper ?? "",
  }));

  const headers = ["date", "forecast", "lower", "upper"];

  const csv = [
    headers.join(","),
    ...rows.map((row) =>
      headers
        .map((header) => {
          const value = row[header];

          if (
            typeof value === "string" &&
            value.includes(",")
          ) {
            return `"${value.replace(/"/g, '""')}"`;
          }

          return value;
        })
        .join(",")
    ),
  ].join("\n");

  const blob = new Blob([csv], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = `${selectedModel}_forecast.csv`;

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);

  showToast("Forecast CSV exported successfully.");
}
async function handleValidation() {
  setValidationLoading(true);
  setValidationError("");

  try {
    const response = await fetch(
      "http://localhost:5000/api/validation",
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dataset_id: activeDatasetId || datasetId,
        }),
      }
    );

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(
        result.error ||
          "The backend could not load validation results."
      );
    }

    setValidationResult(result);

    showToast("Model validation results loaded successfully.");
  } catch (error) {
    console.error("Validation error:", error);

    setValidationError(
      error.message ||
        "Unable to load model validation results."
    );
  } finally {
    setValidationLoading(false);
  }
}


/* ==========================================================
   EXPLAINABILITY + REPORTING
========================================================== */

async function handleExplainability() {
  setExplainLoading(true);
  setExplainError("");

  try {
    const currentDatasetId = activeDatasetId || datasetId;

    if (!currentDatasetId) {
      throw new Error(
        "No active dataset is available. Upload a dataset before requesting explainability."
      );
    }

    const response = await fetch(
      "http://localhost:5000/api/explainability",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          dataset_id: currentDatasetId,
          model: selectedModel,
          target_column: targetColumn,
        }),
      }
    );

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(
        result.error ||
          "The explainability service did not return a valid result."
      );
    }

    setExplainResult(result.analysis || result);
    showToast("Explainability analysis loaded successfully.");
  } catch (error) {
    console.error("Explainability error:", error);
    setExplainError(
      error.message ||
        "Explainability is not available from the backend yet."
    );
  } finally {
    setExplainLoading(false);
  }
}

async function handleExportReportJson() {
    setReportLoading(true);

    try {
      const report = {
        generated_at: new Date().toISOString(),
        application: "ForecastIQ",
        dataset: {
          filename: selectedFile?.name || null,
          dataset_id: activeDatasetId || datasetId || null,
          rows: datasetProfile?.rows ?? quality.rows ?? null,
          columns: datasetProfile?.columns ?? quality.columns ?? null,
          date_column: dateColumn || null,
          target_column: targetColumn || null,
          date_range:
            datasetProfile?.date_range ||
            quality.dateRange ||
            null,
        },
        data_quality: {
          missing_cells:
            datasetProfile?.missing_cells ??
            quality.missing ??
            null,
          duplicate_rows:
            datasetProfile?.duplicate_rows ??
            quality.duplicates ??
            null,
          quality_status:
            datasetProfile?.quality_status ??
            null,
          quality_issues:
            datasetProfile?.quality_issues ??
            [],
        },
        exploration: exploreResult
          ? {
              observations: exploreResult.rows_analyzed ?? null,
              first_date: exploreResult.first_date ?? null,
              last_date: exploreResult.last_date ?? null,
              trend: exploreResult.trend ?? null,
              trend_slope: exploreResult.trend_slope ?? null,
              adf_p_value:
                exploreResult.adf?.p_value ??
                exploreResult.adf_p_value ??
                null,
              stationary:
                exploreResult.adf?.stationary ??
                exploreResult.stationary ??
                null,
            }
          : null,
        anomalies: anomalyResult
          ? {
              summary: anomalyResult.summary ?? {},
              sectors: anomalyResult.sector_summary ?? [],
              timeline_count:
                anomalyResult.timeline?.length ?? 0,
            }
          : null,
        validation: validationResult
          ? {
              methodology:
                validationResult.methodology ?? null,
              walk_forward:
                validationResult.walk_forward ?? [],
              final_test:
                validationResult.final_test ?? [],
            }
          : null,
        forecast: modelResult
          ? {
              model:
                modelResult.model?.name ??
                modelResult.model?.type ??
                selectedModel,
              horizon:
                modelResult.forecast?.length ??
                modelResult.model?.horizon ??
                null,
              forecast: modelResult.forecast ?? [],
              aic: modelResult.aic ?? null,
              bic: modelResult.bic ?? null,
              parameters:
                modelResult.parameters ??
                modelResult.model?.parameters ??
                {},
            }
          : null,
        explainability: explainResult ?? null,
      };

      const response = await fetch(
        "http://localhost:5000/api/report",
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(report),
        }
      );

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(
          result.error ||
            "The reporting service could not generate the report."
        );
      }

      const reportInfo = result.report;

      if (reportInfo?.download_pdf) {
        const pdfUrl =
          `http://localhost:5000${reportInfo.download_pdf}`;

        const pdfResponse = await fetch(pdfUrl, {
          credentials: "include",
        });

        if (pdfResponse.ok) {
          const pdfBlob = await pdfResponse.blob();
          const pdfObjectUrl =
            URL.createObjectURL(pdfBlob);

          const pdfLink =
            document.createElement("a");

          pdfLink.href = pdfObjectUrl;
          pdfLink.download =
            "ForecastIQ_Business_Report.pdf";

          document.body.appendChild(pdfLink);
          pdfLink.click();
          document.body.removeChild(pdfLink);

          URL.revokeObjectURL(pdfObjectUrl);
        }
      }

      if (reportInfo?.download_json) {
        const jsonUrl =
          `http://localhost:5000${reportInfo.download_json}`;

        const jsonResponse = await fetch(jsonUrl, {
          credentials: "include",
        });

        if (jsonResponse.ok) {
          const jsonBlob = await jsonResponse.blob();
          const jsonObjectUrl =
            URL.createObjectURL(jsonBlob);

          const jsonLink =
            document.createElement("a");

          jsonLink.href = jsonObjectUrl;
          jsonLink.download =
            "ForecastIQ_Business_Report.json";

          document.body.appendChild(jsonLink);
          jsonLink.click();
          document.body.removeChild(jsonLink);

          URL.revokeObjectURL(jsonObjectUrl);
        }
      }

      showToast(
        "ForecastIQ management report generated: PDF and JSON exported."
      );
    } catch (error) {
      console.error(
        "Report generation error:",
        error
      );

      showToast(
        error.message ||
          "Unable to generate the business report.",
        "info"
      );
    } finally {
      setReportLoading(false);
    }
  }

function handlePrintReport() {
  window.print();
}

function handleResetAnalysis() {
  setExploreResult(null);
  setExploreError("");
  setAnomalyResult(null);
  setAnomalyError("");
  setModelResult(null);
  setModelError("");
  setValidationResult(null);
  setValidationError("");
  setExplainResult(null);
  setExplainError("");

  showToast(
    "Analysis results cleared. The uploaded dataset remains available.",
    "info"
  );
}

function getModelDisplayName(modelId) {
  const names = {
    tesm: "TESM / Holt-Winters",
    sarima: "SARIMA",
    sarimax: "SARIMAX",
    random_forest: "Random Forest",
    xgboost: "XGBoost",
    lstm: "LSTM",
    gru: "GRU",
  };

  return names[modelId] || modelId;
}

  /* ==========================================================
     DEMO DATASET
  ========================================================== */

  function loadDemoDataset() {
    setIsLoading(true);
    setUploadError("");

    setTimeout(() => {
      setSelectedFile({
        name: "iip_food_products_baseline_2012_2025.csv",
        size: 18432,
        type: "text/csv",
      });

      setDatasetLoaded(true);

      setDatasetColumns([
        "date",
        "year",
        "month",
        "index",
        "growth_rate",
      ]);

      setDateColumn("date");
      setTargetColumn("index");

      setRows(demoRows);

      setQuality({
        rows: 156,
        columns: 5,
        missing: 1,
        duplicates: 0,
        numericColumns: 3,
        dateRange: "Apr 2012 – Mar 2025",
      });
      setDatasetProfile({
  rows: 156,
  columns: 5,
  column_names: [
    "date",
    "year",
    "month",
    "index",
    "growth_rate",
  ],
  numeric_columns: [
    "year",
    "month",
    "index",
    "growth_rate",
  ],
  date_columns: ["date"],
  missing_cells: 1,
  missing_columns: {
    growth_rate: 1,
  },
  duplicate_rows: 0,
  date_range: "2012-04-01 – 2025-03-01",
  first_date: "2012-04-01",
  last_date: "2025-03-01",
  frequency: "MONTHLY",
  quality_status: "ATTENTION",
  quality_issues: [
    "Missing values detected",
  ],
  column_profiles: [],
});

      setShowDataWorkspace(true);

      setIsLoading(false);

      showToast("MoSPI Food Products IIP demo dataset loaded.");
    }, 600);
  }


async function loadAdminOverview() {
  if (authUser?.role !== "admin") {
    return;
  }

  setAdminLoading(true);
  setAdminError("");

  try {
    const response = await fetch(
      "http://localhost:5000/api/admin/overview",
      {
        method: "GET",
        credentials: "include",
      },
    );

    const result = await response.json().catch(() => ({}));

    if (!response.ok || !result.success) {
      throw new Error(
        result.error || "Unable to load the administrative dashboard.",
      );
    }

    setAdminOverview(result);
  } catch (error) {
    console.error("Administrative dashboard error:", error);
    setAdminError(
      error.message || "Unable to load administrative information.",
    );
  } finally {
    setAdminLoading(false);
  }
}

async function updateUserStatus(userId, isActive) {
  try {
    const response = await fetch(
      `http://localhost:5000/api/admin/users/${userId}/status`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ is_active: isActive }),
      },
    );

    const result = await response.json().catch(() => ({}));

    if (!response.ok || !result.success) {
      throw new Error(result.error || "Unable to update user status.");
    }

    setAdminOverview((current) => {
      if (!current) return current;
      return {
        ...current,
        users: (current.users || []).map((user) =>
          user.id === userId ? result.user : user,
        ),
        summary: {
          ...current.summary,
          active_users:
            current.summary.active_users + (isActive ? 1 : -1),
          inactive_users:
            current.summary.inactive_users + (isActive ? -1 : 1),
        },
      };
    });

    showToast(
      isActive
        ? "User account activated."
        : "User account deactivated.",
    );
  } catch (error) {
    console.error("User status update error:", error);
    showToast(error.message || "Unable to update user status.", "info");
  }
}

useEffect(() => {
  if (activePage === "ADMIN" && authUser?.role === "admin") {
    loadAdminOverview();
  }
}, [activePage, authUser?.role]);

  /* ==========================================================
     RESET DATASET
  ========================================================== */

function resetDataset() {
  setSelectedFile(null);
  setDatasetLoaded(false);
  setShowDataWorkspace(false);
  setUploadError("");
  setDatasetProfile(null);
  setDatasetId(null);
  setActiveDatasetId(null);
  setRows(demoRows);

  showToast("Dataset selection cleared.", "info");
}
  /* ==========================================================
     NAVIGATION
  ========================================================== */

  function navigateTo(page) {
    setActivePage(page);
    setMobileMenuOpen(false);

    if (page === "DATA") {
      setShowDataWorkspace(datasetLoaded);
    }
  }

  /* ==========================================================
     DATA QUALITY
  ========================================================== */

  const qualityItems = [
    {
      label: "Rows",
      value: quality.rows,
      status: "good",
    },
    {
      label: "Columns",
      value: quality.columns,
      status: "good",
    },
    {
      label: "Missing values",
      value: quality.missing,
      status: quality.missing === 0 ? "good" : "warning",
    },
    {
      label: "Duplicates",
      value: quality.duplicates,
      status: quality.duplicates === 0 ? "good" : "warning",
    },
  ];

  /* ==========================================================
     PAGE TITLE
  ========================================================== */

  const pageTitle = {
    DATA: "Business Forecasting Workspace",
    PROFILE: "Data Quality",
    CLEAN: "Prepare Your Data",
    EXPLORE: "Understand Your Business Trend",
    ANOMALIES: "Detect Unusual Activity",
    MODELS: "Forecasting Models",
    VALIDATE: "Model Validation",
    FORECAST: "Business Forecast",
    EXPLAIN: "Why This Forecast?",
    REPORT: "Business Reports",
    ADMIN: "Administration",
  };

  const pageDescription = {
    DATA: "Upload historical business data and choose what you want to forecast.",
    PROFILE: "Check whether your dataset is complete, consistent, and ready for forecasting.",
    CLEAN: "Resolve data-quality issues before using the forecasting engine.",
    EXPLORE: "Understand historical trends, seasonality, and statistical patterns before planning ahead.",
    ANOMALIES: "Identify unusual periods and structural changes that may affect planning.",
    MODELS: "Compare statistical and machine-learning forecasting approaches for your dataset.",
    VALIDATE: "Measure historical forecasting performance using time-aware backtesting.",
    FORECAST: "Generate future predictions and planning signals from the selected forecasting models.",
    EXPLAIN: "Understand which model features contributed to the forecast output.",
    REPORT: "Create a shareable business summary of data quality, models, forecasts, and insights.",
    ADMIN: "Review user access, activity, reports, datasets, and system status without exposing credentials.",
  };

  /* ==========================================================
     RENDER
  ========================================================== */

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f7f7f8] px-6">
        <div className="flex flex-col items-center gap-4">
          <ForecastIQLogo size={52} />
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-600">
            <Loader2 className="h-4 w-4 animate-spin text-red-600" />
            Checking your session...
          </div>
        </div>
      </div>
    );
  }

  if (!authUser) {
    return (
      <div className="min-h-screen bg-[#f7f7f8] px-4 py-8 text-gray-900 sm:px-6 lg:px-8">
        <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-6xl items-center justify-center">
          <div className="grid w-full overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-xl lg:grid-cols-[1.05fr_0.95fr]">
            <div className="relative hidden overflow-hidden bg-gray-950 p-10 text-white lg:flex lg:flex-col lg:justify-between">
              <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-red-600/20 blur-3xl" />
              <div className="absolute -bottom-32 -left-20 h-80 w-80 rounded-full bg-red-500/10 blur-3xl" />

              <div className="relative">
                <div className="flex items-center gap-3">
                  <ForecastIQLogo size={46} />
                  <div>
                    <p className="text-base font-bold tracking-wide">ForecastIQ</p>
                    <p className="text-xs text-gray-400">Business Forecasting Platform</p>
                  </div>
                </div>

                <div className="mt-20 max-w-lg">
                  <p className="text-xs font-bold tracking-[0.22em] text-red-400">
                    AI-ENHANCED FORECASTING
                  </p>
                  <h1 className="mt-4 text-4xl font-bold leading-tight tracking-tight">
                    Turn historical data into forward-looking decisions.
                  </h1>
                  <p className="mt-5 text-sm leading-7 text-gray-400">
                    ForecastIQ combines statistical forecasting, machine learning,
                    validation, anomaly detection, and explainability in one workspace.
                  </p>
                </div>
              </div>

              <div className="relative grid grid-cols-3 gap-3">
                {[
                  ["07", "Forecasting models"],
                  ["WF", "Walk-forward validation"],
                  ["SHAP", "Model explainability"],
                ].map(([value, label]) => (
                  <div key={label} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <p className="text-sm font-bold text-white">{value}</p>
                    <p className="mt-1 text-[10px] leading-4 text-gray-400">{label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 sm:p-10 lg:p-12">
              <div className="mx-auto max-w-md">
                <div className="flex items-center gap-3 lg:hidden">
                  <ForecastIQLogo size={42} />
                  <div>
                    <p className="text-sm font-bold">ForecastIQ</p>
                    <p className="text-[10px] text-gray-500">Business Forecasting Platform</p>
                  </div>
                </div>

                <div className="mt-8 lg:mt-0">
                  <p className="text-xs font-bold tracking-[0.18em] text-red-600">
                    SECURE WORKSPACE
                  </p>
                  <h2 className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
                    {authMode === "login"
                      ? "Welcome back"
                      : authMode === "register"
                      ? "Create your account"
                      : authMode === "forgot"
                      ? "Forgot your password?"
                      : "Reset your password"}
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-gray-500">
                    {authMode === "login"
                      ? "Sign in to access your ForecastIQ workspace."
                      : authMode === "register"
                      ? "Create a user account to start working with your forecasting workspace."
                      : authMode === "forgot"
                      ? "Enter your registered email address to receive a one-time reset code."
                      : "Enter the reset code and choose a new password."}
                  </p>
                </div>

                {(authMode === "login" || authMode === "register") ? (
                  <div className="mt-7 grid grid-cols-2 rounded-xl bg-gray-100 p-1">
                    <button
                      type="button"
                      onClick={() => switchAuthMode("login")}
                      className={`rounded-lg px-4 py-2.5 text-xs font-bold transition ${
                        authMode === "login"
                          ? "bg-white text-gray-900 shadow-sm"
                          : "text-gray-500 hover:text-gray-800"
                      }`}
                    >
                      Sign in
                    </button>
                    <button
                      type="button"
                      onClick={() => switchAuthMode("register")}
                      className={`rounded-lg px-4 py-2.5 text-xs font-bold transition ${
                        authMode === "register"
                          ? "bg-white text-gray-900 shadow-sm"
                          : "text-gray-500 hover:text-gray-800"
                      }`}
                    >
                      Register
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => switchAuthMode("login")}
                    className="mt-7 inline-flex items-center gap-2 text-xs font-bold text-gray-500 transition hover:text-gray-900"
                  >
                    ← Back to sign in
                  </button>
                )}

                {authError && (
                  <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />
                    <p className="text-xs font-medium leading-5 text-red-700">{authError}</p>
                  </div>
                )}

                {authMode === "forgot" ? (
                  <form onSubmit={handleForgotPassword} className="mt-6 space-y-4">
                    <div>
                      <label className="mb-2 block text-xs font-bold text-gray-700">Email address</label>
                      <div className="relative">
                        <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                        <input
                          type="email"
                          value={authForm.email}
                          onChange={(event) => updateAuthField("email", event.target.value)}
                          placeholder="you@example.com"
                          autoComplete="email"
                          className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-10 pr-4 text-sm outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                          required
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={authSubmitting}
                      className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-red-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-red-600/20 transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {authSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mail className="h-4 w-4" />}
                      {authSubmitting ? "Sending code..." : "Send reset code"}
                    </button>
                  </form>
                ) : authMode === "reset" ? (
                  <form onSubmit={handleResetPassword} className="mt-6 space-y-4">
                    {resetMessage && (
                      <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-xs leading-5 text-green-700">
                        {resetMessage}
                      </div>
                    )}

                    <div>
                      <label className="mb-2 block text-xs font-bold text-gray-700">6-digit reset code</label>
                      <input
                        type="text"
                        inputMode="numeric"
                        maxLength={6}
                        value={resetCode}
                        onChange={(event) => setResetCode(event.target.value.replace(/\D/g, "").slice(0, 6))}
                        placeholder="123456"
                        className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm tracking-[0.3em] outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                        required
                      />
                    </div>

                    <div>
                      <label className="mb-2 block text-xs font-bold text-gray-700">New password</label>
                      <input
                        type="password"
                        value={resetPassword}
                        onChange={(event) => setResetPassword(event.target.value)}
                        autoComplete="new-password"
                        placeholder="Create a new password"
                        className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                        required
                      />
                      <p className="mt-2 text-[10px] leading-4 text-gray-400">
                        Minimum 8 characters with uppercase, lowercase, number, and special character.
                      </p>
                    </div>

                    <div>
                      <label className="mb-2 block text-xs font-bold text-gray-700">Confirm new password</label>
                      <input
                        type="password"
                        value={resetConfirmPassword}
                        onChange={(event) => setResetConfirmPassword(event.target.value)}
                        autoComplete="new-password"
                        placeholder="Re-enter your new password"
                        className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                        required
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={authSubmitting}
                      className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-red-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-red-600/20 transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {authSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <LockKeyhole className="h-4 w-4" />}
                      {authSubmitting ? "Resetting password..." : "Reset password"}
                    </button>
                  </form>
                ) : (
                  <form onSubmit={handleAuthSubmit} className="mt-6 space-y-4">
                    {authMode === "register" && (
                      <div>
                        <label className="mb-2 block text-xs font-bold text-gray-700">Full name</label>
                        <div className="relative">
                          <UserRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                          <input
                            type="text"
                            value={authForm.name}
                            onChange={(event) => updateAuthField("name", event.target.value)}
                            placeholder="Your name"
                            autoComplete="name"
                            className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-10 pr-4 text-sm outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                            required
                          />
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="mb-2 block text-xs font-bold text-gray-700">Email address</label>
                      <div className="relative">
                        <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                        <input
                          type="email"
                          value={authForm.email}
                          onChange={(event) => updateAuthField("email", event.target.value)}
                          placeholder="you@example.com"
                          autoComplete="email"
                          className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-10 pr-4 text-sm outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="mb-2 block text-xs font-bold text-gray-700">Password</label>
                      <div className="relative">
                        <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                        <input
                          type={showPassword ? "text" : "password"}
                          value={authForm.password}
                          onChange={(event) => updateAuthField("password", event.target.value)}
                          placeholder="Enter your password"
                          autoComplete={authMode === "login" ? "current-password" : "new-password"}
                          className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-10 pr-11 text-sm outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword((current) => !current)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700"
                          aria-label={showPassword ? "Hide password" : "Show password"}
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                      {authMode === "register" && (
                        <p className="mt-2 text-[10px] leading-4 text-gray-400">
                          Minimum 8 characters with uppercase, lowercase, number, and special character.
                        </p>
                      )}
                    </div>

                    {authMode === "register" && (
                      <div>
                        <label className="mb-2 block text-xs font-bold text-gray-700">Confirm password</label>
                        <div className="relative">
                          <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                          <input
                            type={showConfirmPassword ? "text" : "password"}
                            value={authForm.confirmPassword}
                            onChange={(event) => updateAuthField("confirmPassword", event.target.value)}
                            placeholder="Re-enter your password"
                            autoComplete="new-password"
                            className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-10 pr-11 text-sm outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-50"
                            required
                          />
                          <button
                            type="button"
                            onClick={() => setShowConfirmPassword((current) => !current)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700"
                            aria-label={showConfirmPassword ? "Hide confirmation password" : "Show confirmation password"}
                          >
                            {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                      </div>
                    )}

                    {authMode === "login" && (
                      <div className="-mt-1 text-right">
                        <button
                          type="button"
                          onClick={() => switchAuthMode("forgot")}
                          className="text-xs font-bold text-red-600 transition hover:text-red-700"
                        >
                          Forgot password?
                        </button>
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={authSubmitting}
                      className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-red-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-red-600/20 transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {authSubmitting ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          {authMode === "register" ? "Creating account..." : "Signing in..."}
                        </>
                      ) : authMode === "register" ? (
                        "Create account"
                      ) : (
                        "Sign in"
                      )}
                    </button>
                  </form>
                )}

                <div className="mt-7 border-t border-gray-100 pt-5">
                  <p className="text-center text-[10px] leading-5 text-gray-400">
                    Your password is never displayed or stored as plaintext.
                    ForecastIQ stores a password hash in the database.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7f7f8] text-gray-900">

      {/* ======================================================
          TOAST
      ====================================================== */}

      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="fixed right-5 top-5 z-[100] flex max-w-sm items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-xl"
          >
            {toast.type === "success" ? (
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            ) : (
              <Info className="h-5 w-5 text-red-600" />
            )}

            <span className="text-xs font-semibold text-gray-700">
              {toast.message}
            </span>

            <button
              onClick={() => setToast(null)}
              className="ml-2 text-gray-400 hover:text-gray-700"
            >
              <X className="h-4 w-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

<div className="flex h-screen overflow-hidden bg-[#f7f7f8]">

  {/* ====================================================
      LEFT WORKFLOW PANEL
  ==================================================== */}

  <aside className="hidden w-72 shrink-0 border-r border-gray-200 bg-white lg:flex lg:flex-col">

    {/* BRAND */}
    <div className="shrink-0 border-b border-gray-200 p-5">

      <div className="flex items-center gap-3">

        <ForecastIQLogo size={40} />

        <div>
          <h1 className="text-sm font-bold tracking-wide text-gray-900">
            ForecastIQ
          </h1>

          <p className="text-xs text-gray-500">
            Business Forecasting Platform
          </p>
        </div>

      </div>

    </div>


    {/* WORKFLOW NAVIGATION */}
    <div className="flex-1 overflow-y-auto p-4">

      <div className="mb-4 px-3">

        <p className="text-[10px] font-bold tracking-[0.18em] text-gray-400">
          BUSINESS FORECASTING
        </p>

        <p className="mt-1 text-[10px] text-gray-400">
          From raw data to planning insights
        </p>

      </div>


      <nav className="space-y-1.5">

        {navigation.filter((item) => item.label !== "ADMIN" || authUser?.role === "admin").map((item, index) => {

          const Icon = item.icon;
          const active = activePage === item.label;

          return (
            <button
              key={item.label}
              onClick={() => navigateTo(item.label)}
              className={`group relative flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition-all ${
                active
                  ? "bg-red-50 text-red-700"
                  : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >

              {/* STEP NUMBER */}
              <span
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[10px] font-bold ${
                  active
                    ? "bg-red-600 text-white"
                    : "bg-gray-100 text-gray-400 group-hover:bg-gray-200 group-hover:text-gray-600"
                }`}
              >
                {String(index + 1).padStart(2, "0")}
              </span>


              {/* ICON */}
              <Icon
                className={`h-4 w-4 shrink-0 ${
                  active
                    ? "text-red-600"
                    : "text-gray-400 group-hover:text-gray-700"
                }`}
              />


              {/* LABEL */}
              <div className="min-w-0 flex-1">

                <p
                  className={`text-xs font-bold tracking-wide ${
                    active
                      ? "text-red-700"
                      : "text-gray-600 group-hover:text-gray-900"
                  }`}
                >
                  {item.title || item.label}
                </p>

                <p className="mt-0.5 truncate text-[9px] text-gray-400">
                  {workflow[index]?.[2]}
                </p>

              </div>


              {/* ACTIVE INDICATOR */}
              {active && (
                <span className="h-2 w-2 shrink-0 rounded-full bg-red-600 shadow-sm" />
              )}

            </button>
          );

        })}

      </nav>

    </div>


    {/* SYSTEM STATUS */}
    <div className="shrink-0 border-t border-gray-200 p-4">

      <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">

        <div className="mb-3 flex items-center gap-2">

          <ShieldCheck className="h-4 w-4 text-green-600" />

          <span className="text-xs font-bold text-gray-700">
            SYSTEM STATUS
          </span>

        </div>

        <div className="flex items-center gap-2">

          <span className="h-2 w-2 rounded-full bg-green-500" />

          <span className="text-xs text-gray-500">
            All systems operational
          </span>

        </div>

      </div>

    </div>

  </aside>


  {/* ====================================================
      RIGHT WORKSPACE
  ==================================================== */}

  <main className="min-w-0 flex-1 overflow-y-auto">

    {/* ==================================================
        TOP HEADER
    ================================================== */}

    <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between border-b border-gray-200 bg-white/95 px-5 backdrop-blur-xl lg:px-8">

      <div className="flex items-center gap-3">

        {/* MOBILE MENU */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="rounded-lg border border-gray-200 bg-white p-2 text-gray-600 lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>


        <div>

          <p className="text-[10px] font-bold tracking-[0.22em] text-red-600">
            FORECASTIQ ANALYTICS
          </p>

          <h2 className="mt-1 text-sm font-semibold text-gray-800">
            {pageTitle[activePage]}
          </h2>

        </div>

      </div>


      <div className="flex items-center gap-3">

        {/* SYSTEM INDICATOR */}
        <div className="hidden items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-3 py-1.5 sm:flex">

          <span
            className={`h-1.5 w-1.5 rounded-full ${
              isLoading ? "bg-yellow-500" : "bg-green-500"
            }`}
          />

          <span className="text-[11px] font-medium text-gray-600">
            {isLoading ? "Processing" : "System Ready"}
          </span>

        </div>


        {/* CURRENT USER */}
        <div className="hidden items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-1.5 sm:flex">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-50">
            <UserRound className="h-3.5 w-3.5 text-red-600" />
          </div>
          <div className="max-w-[150px]">
            <p className="truncate text-[11px] font-bold text-gray-800">
              {authUser?.name || authUser?.email}
            </p>
            <p className="text-[9px] font-semibold uppercase tracking-wider text-gray-400">
              {authUser?.role || "user"}
            </p>
          </div>
        </div>

        {/* SETTINGS */}
        <button className="rounded-lg border border-gray-200 bg-white p-2 text-gray-500 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600">
          <Settings2 className="h-4 w-4" />
        </button>

        {/* LOGOUT */}
        <button
          type="button"
          onClick={handleLogout}
          title="Sign out"
          className="rounded-lg border border-gray-200 bg-white p-2 text-gray-500 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
        >
          <LogOut className="h-4 w-4" />
        </button>

      </div>

    </header>
    {/* ==================================================
        MOBILE NAVIGATION
    ================================================== */}

    <AnimatePresence>
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="border-b border-gray-200 bg-white p-4 lg:hidden"
        >
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">

            {navigation.filter((item) => item.label !== "ADMIN" || authUser?.role === "admin").map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.label}
                  onClick={() => navigateTo(item.label)}
                  className={`flex items-center gap-2 rounded-lg border px-3 py-2.5 text-left text-[10px] font-bold ${
                    activePage === item.label
                      ? "border-red-200 bg-red-50 text-red-700"
                      : "border-gray-200 bg-gray-50 text-gray-600"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  {item.title || item.label}
                </button>
              );
            })}

          </div>
        </motion.div>
      )}
    </AnimatePresence>


    {/* ==================================================
        PAGE CONTENT
    ================================================== */}

    <section className="mx-auto max-w-7xl p-5 lg:p-8">
            {/* =================================================
                PAGE HEADER
            ================================================= */}

            {activePage === "PROFILE" && (
      <motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  className="space-y-6"
>
  {/* =====================================================
      PROFILE OVERVIEW
  ====================================================== */}

  <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:p-8">

    <div className="flex items-start gap-4">

      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-red-50">
        <BarChart3 className="h-5 w-5 text-red-600" />
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-900">
          Dataset Profile
        </h3>

        <p className="mt-1 text-sm text-gray-500">
          Structural analysis and initial data-quality assessment.
        </p>
      </div>

    </div>

    {datasetProfile ? (
      <>
        {/* =================================================
            OVERVIEW CARDS
        ================================================== */}

        <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
            <p className="text-[10px] font-bold tracking-wider text-gray-400">
              ROWS
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {datasetProfile.rows.toLocaleString()}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Observations
            </p>
          </div>

          <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
            <p className="text-[10px] font-bold tracking-wider text-gray-400">
              COLUMNS
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {datasetProfile.columns}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Variables
            </p>
          </div>

          <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
            <p className="text-[10px] font-bold tracking-wider text-gray-400">
              FREQUENCY
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {datasetProfile.frequency || "—"}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Detected frequency
            </p>
          </div>

          <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
            <p className="text-[10px] font-bold tracking-wider text-gray-400">
              MISSING
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {datasetProfile.missing_cells}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Missing cells
            </p>
          </div>

        </div>


        {/* =================================================
            COVERAGE + QUALITY
        ================================================== */}

        <div className="mt-5 grid gap-5 lg:grid-cols-2">

          <div className="rounded-xl border border-gray-200 bg-white p-5">

            <p className="text-[10px] font-bold tracking-wider text-gray-400">
              TIME COVERAGE
            </p>

            <p className="mt-3 text-lg font-bold text-gray-900">
              {datasetProfile.date_range || "Not detected"}
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3">

              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-[9px] font-semibold text-gray-400">
                  START
                </p>

                <p className="mt-1 text-xs font-bold text-gray-700">
                  {datasetProfile.first_date || "—"}
                </p>
              </div>

              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-[9px] font-semibold text-gray-400">
                  END
                </p>

                <p className="mt-1 text-xs font-bold text-gray-700">
                  {datasetProfile.last_date || "—"}
                </p>
              </div>

            </div>

          </div>


          <div className="rounded-xl border border-gray-200 bg-white p-5">

            <div className="flex items-center justify-between">

              <div>
                <p className="text-[10px] font-bold tracking-wider text-gray-400">
                  DATA QUALITY
                </p>

                <p className="mt-1 text-sm font-bold text-gray-900">
                  Initial validation
                </p>
              </div>

              <span
                className={`rounded-full border px-3 py-1 text-[10px] font-bold ${
                  datasetProfile.quality_status === "GOOD"
                    ? "border-green-200 bg-green-50 text-green-700"
                    : "border-yellow-200 bg-yellow-50 text-yellow-700"
                }`}
              >
                {datasetProfile.quality_status}
              </span>

            </div>


            <div className="mt-4 space-y-2">

              {(datasetProfile.quality_issues?.length
                ? datasetProfile.quality_issues
                : ["No quality issues detected."]
              ).map((issue, index) => (

                <div
                  key={index}
                  className="flex items-center gap-2 rounded-lg bg-gray-50 px-3 py-2"
                >
                  <AlertTriangle className="h-3.5 w-3.5 text-yellow-600" />

                  <span className="text-xs text-gray-600">
                    {issue}
                  </span>
                </div>

              ))}

            </div>

          </div>

        </div>

      </>
    ) : (

      <div className="mt-7 rounded-xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">

        <Database className="mx-auto h-8 w-8 text-gray-300" />

        <p className="mt-3 text-sm font-semibold text-gray-700">
          No dataset profile available
        </p>

        <p className="mt-1 text-xs text-gray-500">
          Upload a dataset from the DATA workspace first.
        </p>

        <button
          onClick={() => navigateTo("DATA")}
          className="mt-5 rounded-lg bg-red-600 px-5 py-2.5 text-xs font-bold text-white transition hover:bg-red-700"
        >
          Go to DATA
        </button>

      </div>

    )}

  </div>


  {/* =====================================================
      COLUMN PROFILE
  ====================================================== */}

  {datasetProfile?.column_profiles?.length > 0 && (

    <div className="rounded-2xl border border-gray-200 bg-white shadow-sm">

      <div className="border-b border-gray-200 p-5">

        <p className="text-xs font-bold tracking-wider text-gray-800">
          COLUMN PROFILE
        </p>

        <p className="mt-1 text-xs text-gray-500">
          Structure and quality information for each variable.
        </p>

      </div>


      <div className="overflow-x-auto">

        <table className="w-full min-w-[850px] text-left">

          <thead className="bg-gray-50">

            <tr>

              <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Column
              </th>

              <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Data Type
              </th>

              <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Missing
              </th>

              <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Missing %
              </th>

              <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Unique
              </th>

              <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Role
              </th>

            </tr>

          </thead>


          <tbody>

            {datasetProfile.column_profiles.map(
              (column, index) => {

                const isDate =
                  datasetProfile.date_columns?.includes(
                    column.name
                  );

                const isNumeric =
                  datasetProfile.numeric_columns?.includes(
                    column.name
                  );

                const isTarget =
                  column.name === targetColumn;

                return (
                  <tr
                    key={column.name}
                    className="border-t border-gray-100 hover:bg-gray-50"
                  >

                    <td className="px-5 py-4">

                      <span className="text-xs font-bold text-gray-800">
                        {column.name}
                      </span>

                    </td>

                    <td className="px-5 py-4">
                      <span className="rounded-md bg-gray-100 px-2 py-1 text-[10px] font-semibold text-gray-600">
                        {column.dtype}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-xs text-gray-600">
                      {column.missing}
                    </td>

                    <td className="px-5 py-4 text-xs text-gray-600">
                      {column.missing_percentage}%
                    </td>

                    <td className="px-5 py-4 text-xs text-gray-600">
                      {column.unique.toLocaleString()}
                    </td>

                    <td className="px-5 py-4">

                      {isTarget ? (
                        <span className="rounded-full bg-red-50 px-2.5 py-1 text-[10px] font-bold text-red-700">
                          TARGET
                        </span>
                      ) : isDate ? (
                        <span className="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-bold text-blue-700">
                          DATE
                        </span>
                      ) : isNumeric ? (
                        <span className="rounded-full bg-gray-100 px-2.5 py-1 text-[10px] font-bold text-gray-600">
                          NUMERIC
                        </span>
                      ) : (
                        <span className="rounded-full bg-gray-100 px-2.5 py-1 text-[10px] font-bold text-gray-500">
                          OTHER
                        </span>
                      )}

                    </td>

                  </tr>
                );
              }
            )}

          </tbody>

        </table>

      </div>

    </div>

  )}


  {/* =====================================================
      NUMERIC STATISTICS
  ====================================================== */}

  {datasetProfile?.column_profiles?.some(
    (column) => column.statistics
  ) && (

    <div className="rounded-2xl border border-gray-200 bg-white shadow-sm">

      <div className="border-b border-gray-200 p-5">

        <p className="text-xs font-bold tracking-wider text-gray-800">
          NUMERIC STATISTICS
        </p>

        <p className="mt-1 text-xs text-gray-500">
          Descriptive statistics for numeric variables.
        </p>

      </div>


      <div className="grid gap-4 p-5 md:grid-cols-2">

        {datasetProfile.column_profiles
          .filter(
            (column) => column.statistics
          )
          .map((column) => (

            <div
              key={column.name}
              className="rounded-xl border border-gray-200 bg-gray-50 p-5"
            >

              <div className="flex items-center justify-between">

                <p className="text-sm font-bold text-gray-900">
                  {column.name}
                </p>

                {column.name === targetColumn && (
                  <span className="rounded-full bg-red-50 px-2.5 py-1 text-[9px] font-bold text-red-700">
                    TARGET
                  </span>
                )}

              </div>


              <div className="mt-5 grid grid-cols-2 gap-3">

                <div className="rounded-lg bg-white p-3">
                  <p className="text-[9px] font-semibold text-gray-400">
                    MEAN
                  </p>

                  <p className="mt-1 text-sm font-bold text-gray-800">
                    {column.statistics.mean}
                  </p>
                </div>

                <div className="rounded-lg bg-white p-3">
                  <p className="text-[9px] font-semibold text-gray-400">
                    MEDIAN
                  </p>

                  <p className="mt-1 text-sm font-bold text-gray-800">
                    {column.statistics.median}
                  </p>
                </div>

                <div className="rounded-lg bg-white p-3">
                  <p className="text-[9px] font-semibold text-gray-400">
                    STD DEV
                  </p>

                  <p className="mt-1 text-sm font-bold text-gray-800">
                    {column.statistics.std}
                  </p>
                </div>

                <div className="rounded-lg bg-white p-3">
                  <p className="text-[9px] font-semibold text-gray-400">
                    MIN
                  </p>

                  <p className="mt-1 text-sm font-bold text-gray-800">
                    {column.statistics.min}
                  </p>
                </div>

                <div className="rounded-lg bg-white p-3">
                  <p className="text-[9px] font-semibold text-gray-400">
                    MAX
                  </p>

                  <p className="mt-1 text-sm font-bold text-gray-800">
                    {column.statistics.max}
                  </p>
                </div>

                <div className="rounded-lg bg-white p-3">
                  <p className="text-[9px] font-semibold text-gray-400">
                    UNIQUE
                  </p>

                  <p className="mt-1 text-sm font-bold text-gray-800">
                    {column.unique.toLocaleString()}
                  </p>
                </div>

              </div>

            </div>

          ))}

      </div>

    </div>

  )}


  {/* =====================================================
      CONTINUE
  ====================================================== */}

  {datasetProfile && (

    <div className="flex justify-end">

      <button
        onClick={() => {
          setActivePage("CLEAN");
          showToast("Profile analysis completed.");
        }}
        className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-6 py-3 text-xs font-bold text-white shadow-sm transition hover:bg-red-700"
      >
        Continue to Clean
        <ChevronRight className="h-4 w-4" />
      </button>

    </div>

  )}

</motion.div>
    )}

{/* =================================================
    CLEAN DATA
================================================= */}

{activePage === "CLEAN" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4 }}
    className="space-y-6"
  >

    {/* =================================================
        PAGE INTRO
    ================================================== */}

    <div>
      <p className="text-xs font-bold tracking-[0.18em] text-red-600">
        DATA PREPARATION
      </p>

      <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
        Clean your dataset
      </h1>

      <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-500">
        Prepare the uploaded time-series data before exploration and
        forecasting. The original uploaded file remains unchanged.
      </p>
    </div>


    {/* =================================================
        NO DATA STATE
    ================================================== */}

    {!datasetLoaded ? (
      <div className="rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">

        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50">
          <Database className="h-7 w-7 text-red-600" />
        </div>

        <h2 className="mt-5 text-lg font-bold text-gray-900">
          No dataset available
        </h2>

        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
          Upload a CSV or Excel time-series dataset from the DATA
          workspace before configuring the cleaning pipeline.
        </p>

        <button
          type="button"
          onClick={() => navigateTo("DATA")}
          className="mt-6 inline-flex items-center gap-2 rounded-lg bg-red-600 px-5 py-3 text-xs font-bold text-white shadow-sm transition hover:bg-red-700"
        >
          Go to DATA
          <ChevronRight className="h-4 w-4" />
        </button>

      </div>
    ) : (

      <>
        {/* =================================================
            DATASET SUMMARY
        ================================================== */}

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

            <div className="flex items-start gap-3">

              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-50">
                <FileSpreadsheet className="h-5 w-5 text-red-600" />
              </div>

              <div className="min-w-0">

                <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
                  CURRENT DATASET
                </p>

                <p className="mt-1 truncate text-sm font-bold text-gray-900">
                  {selectedFile?.name || "Uploaded dataset"}
                </p>

                <p className="mt-1 text-xs text-gray-500">
                  {quality.rows.toLocaleString()} rows · {quality.columns} columns
                </p>

              </div>

            </div>

            <div className="flex items-center gap-2">

              <span className="inline-flex items-center gap-2 rounded-full border border-green-200 bg-green-50 px-3 py-1.5 text-[10px] font-bold text-green-700">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                DATASET LOADED
              </span>

            </div>

          </div>

        </div>


        {/* =================================================
            COLUMN MAPPING
        ================================================== */}

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="mb-6">

            <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
              COLUMN MAPPING
            </p>

            <h2 className="mt-1 text-lg font-bold text-gray-900">
              Define the time-series structure
            </h2>

            <p className="mt-1 text-xs leading-5 text-gray-500">
              Select the date column and forecasting target used by the
              cleaning and modelling pipeline.
            </p>

          </div>


          <div className="grid gap-5 md:grid-cols-2">

            {/* DATE COLUMN */}
            <div>

              <label
                htmlFor="clean-date-column"
                className="mb-2 block text-xs font-bold text-gray-700"
              >
                Date / Time Column
              </label>

              <select
                id="clean-date-column"
                value={dateColumn}
                onChange={(event) => setDateColumn(event.target.value)}
                className="w-full rounded-lg border border-gray-200 bg-white px-3 py-3 text-sm text-gray-800 outline-none transition focus:border-red-400 focus:ring-2 focus:ring-red-100"
              >
                {datasetColumns.map((column) => (
                  <option key={column} value={column}>
                    {column}
                  </option>
                ))}
              </select>

              <p className="mt-2 text-[11px] text-gray-400">
                Used to preserve chronological ordering.
              </p>

            </div>


            {/* TARGET COLUMN */}
            <div>

              <label
                htmlFor="clean-target-column"
                className="mb-2 block text-xs font-bold text-gray-700"
              >
                Forecast Target
              </label>

              <select
                id="clean-target-column"
                value={targetColumn}
                onChange={(event) => setTargetColumn(event.target.value)}
                className="w-full rounded-lg border border-gray-200 bg-white px-3 py-3 text-sm text-gray-800 outline-none transition focus:border-red-400 focus:ring-2 focus:ring-red-100"
              >
                {datasetColumns.map((column) => (
                  <option key={column} value={column}>
                    {column}
                  </option>
                ))}
              </select>

              <p className="mt-2 text-[11px] text-gray-400">
                Outlier treatment and transformations apply to this target.
              </p>

            </div>

          </div>

        </div>


        {/* =================================================
            CLEANING CONFIGURATION
        ================================================== */}

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="mb-6">

            <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
              CLEANING PIPELINE
            </p>

            <h2 className="mt-1 text-lg font-bold text-gray-900">
              Configure data preparation
            </h2>

            <p className="mt-1 text-xs leading-5 text-gray-500">
              Choose how missing values, duplicates, outliers, and target
              transformations should be handled.
            </p>

          </div>


          <div className="grid gap-5 md:grid-cols-2">

            {/* =================================================
                MISSING VALUES
            ================================================== */}

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">

              <div className="flex items-start gap-3">

                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                </div>

                <div className="min-w-0 flex-1">

                  <label
                    htmlFor="missing-method"
                    className="block text-sm font-bold text-gray-800"
                  >
                    Missing values
                  </label>

                  <p className="mt-1 text-[11px] leading-5 text-gray-500">
                    Choose how missing observations should be handled.
                  </p>

                  <select
                    id="missing-method"
                    value={cleanConfig.missing_method}
                    onChange={(event) =>
                      setCleanConfig((current) => ({
                        ...current,
                        missing_method: event.target.value,
                      }))
                    }
                    className="mt-4 w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-xs font-medium text-gray-700 outline-none focus:border-red-400 focus:ring-2 focus:ring-red-100"
                  >
                    <option value="none">
                      No treatment
                    </option>

                    <option value="drop">
                      Drop rows
                    </option>

                    <option value="ffill">
                      Forward fill
                    </option>

                    <option value="bfill">
                      Backward fill
                    </option>

                    <option value="interpolate">
                      Interpolate
                    </option>
                  </select>

                </div>

              </div>

            </div>


            {/* =================================================
                DUPLICATES
            ================================================== */}

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">

              <div className="flex items-start gap-3">

                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white">
                  <Table2 className="h-4 w-4 text-gray-600" />
                </div>

                <div className="min-w-0 flex-1">

                  <label
                    htmlFor="duplicate-method"
                    className="block text-sm font-bold text-gray-800"
                  >
                    Duplicate rows
                  </label>

                  <p className="mt-1 text-[11px] leading-5 text-gray-500">
                    Decide whether duplicate observations should remain.
                  </p>

                  <select
                    id="duplicate-method"
                    value={cleanConfig.duplicate_method}
                    onChange={(event) =>
                      setCleanConfig((current) => ({
                        ...current,
                        duplicate_method: event.target.value,
                      }))
                    }
                    className="mt-4 w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-xs font-medium text-gray-700 outline-none focus:border-red-400 focus:ring-2 focus:ring-red-100"
                  >
                    <option value="keep">
                      Keep duplicates
                    </option>

                    <option value="remove">
                      Remove duplicates
                    </option>
                  </select>

                </div>

              </div>

            </div>


            {/* =================================================
                OUTLIERS
            ================================================== */}

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">

              <div className="flex items-start gap-3">

                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                </div>

                <div className="min-w-0 flex-1">

                  <label
                    htmlFor="outlier-method"
                    className="block text-sm font-bold text-gray-800"
                  >
                    Target outliers
                  </label>

                  <p className="mt-1 text-[11px] leading-5 text-gray-500">
                    Cap extreme values in the selected forecast target.
                  </p>

                  <select
                    id="outlier-method"
                    value={cleanConfig.outlier_method}
                    onChange={(event) =>
                      setCleanConfig((current) => ({
                        ...current,
                        outlier_method: event.target.value,
                      }))
                    }
                    className="mt-4 w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-xs font-medium text-gray-700 outline-none focus:border-red-400 focus:ring-2 focus:ring-red-100"
                  >
                    <option value="none">
                      No treatment
                    </option>

                    <option value="iqr_cap">
                      IQR capping
                    </option>

                    <option value="robust_zscore_cap">
                      Robust-Z capping
                    </option>
                  </select>

                </div>

              </div>

            </div>


            {/* =================================================
                TRANSFORMATION
            ================================================== */}

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">

              <div className="flex items-start gap-3">

                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white">
                  <RefreshCcw className="h-4 w-4 text-blue-600" />
                </div>

                <div className="min-w-0 flex-1">

                  <label
                    htmlFor="transformation"
                    className="block text-sm font-bold text-gray-800"
                  >
                    Target transformation
                  </label>

                  <p className="mt-1 text-[11px] leading-5 text-gray-500">
                    Apply a transformation to stabilize the target scale.
                  </p>

                  <select
                    id="transformation"
                    value={cleanConfig.transformation}
                    onChange={(event) =>
                      setCleanConfig((current) => ({
                        ...current,
                        transformation: event.target.value,
                      }))
                    }
                    className="mt-4 w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-xs font-medium text-gray-700 outline-none focus:border-red-400 focus:ring-2 focus:ring-red-100"
                  >
                    <option value="none">
                      No transformation
                    </option>

                    <option value="log1p">
                      log1p transformation
                    </option>
                  </select>

                </div>

              </div>

            </div>

          </div>

        </div>


        {/* =================================================
            CURRENT CONFIGURATION
        ================================================== */}

        <div className="rounded-2xl border border-red-100 bg-red-50/50 p-5">

          <div className="flex items-start gap-3">

            <Settings2 className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />

            <div className="min-w-0">

              <p className="text-sm font-bold text-gray-900">
                Cleaning configuration
              </p>

              <div className="mt-3 flex flex-wrap gap-2">

                <span className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-[10px] font-semibold text-gray-600">
                  Missing: {cleanConfig.missing_method}
                </span>

                <span className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-[10px] font-semibold text-gray-600">
                  Duplicates: {cleanConfig.duplicate_method}
                </span>

                <span className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-[10px] font-semibold text-gray-600">
                  Outliers: {cleanConfig.outlier_method}
                </span>

                <span className="rounded-full border border-gray-200 bg-white px-3 py-1.5 text-[10px] font-semibold text-gray-600">
                  Transform: {cleanConfig.transformation}
                </span>

              </div>

            </div>

          </div>

        </div>


        {/* =================================================
            ERROR
        ================================================== */}

        {cleanError && (
          <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4">

            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />

            <div>
              <p className="text-xs font-bold text-red-700">
                Cleaning failed
              </p>

              <p className="mt-1 text-xs leading-5 text-red-600">
                {cleanError}
              </p>
            </div>

          </div>
        )}


        {/* =================================================
            ACTIONS
        ================================================== */}

        <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">

          <button
            type="button"
            onClick={() =>
              setCleanConfig({
                missing_method: "none",
                duplicate_method: "keep",
                outlier_method: "none",
                transformation: "none",
              })
            }
            disabled={cleaning}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white px-5 py-3 text-xs font-bold text-gray-600 transition hover:border-gray-300 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCcw className="h-4 w-4" />
            Reset Options
          </button>


          <button
            type="button"
            onClick={handleCleanDataset}
            disabled={cleaning || !datasetId}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-6 py-3 text-xs font-bold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >

            {cleaning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Cleaning dataset...
              </>
            ) : (
              <>
                <CheckCircle2 className="h-4 w-4" />
                Apply Cleaning
              </>
            )}

          </button>

        </div>


        {/* =================================================
            CLEANING RESULT
        ================================================== */}

        {cleanResult && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-5"
          >

            <div className="rounded-2xl border border-green-200 bg-green-50 p-5">

              <div className="flex items-start gap-3">

                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-600" />

                <div>

                  <p className="text-sm font-bold text-green-800">
                    Dataset cleaned successfully
                  </p>

                  <p className="mt-1 text-xs leading-5 text-green-700">
                    The original uploaded dataset was preserved. The cleaned
                    version has been generated by the backend.
                  </p>

                </div>

              </div>

            </div>


            {/* BEFORE / AFTER */}
            {(cleanResult.before || cleanResult.after) && (
              <div className="grid gap-5 md:grid-cols-2">

                <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">

                  <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
                    BEFORE CLEANING
                  </p>

                  <div className="mt-4 grid grid-cols-2 gap-3">

                    <div className="rounded-lg bg-gray-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        ROWS
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.before?.rows ?? "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-gray-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        MISSING
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.before?.missing_cells ?? "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-gray-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        DUPLICATES
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.before?.duplicate_rows ?? "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-gray-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        COLUMNS
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.before?.columns ?? quality.columns}
                      </p>
                    </div>

                  </div>

                </div>


                <div className="rounded-xl border border-green-200 bg-white p-5 shadow-sm">

                  <p className="text-[10px] font-bold tracking-[0.16em] text-green-600">
                    AFTER CLEANING
                  </p>

                  <div className="mt-4 grid grid-cols-2 gap-3">

                    <div className="rounded-lg bg-green-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        ROWS
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.after?.rows ?? "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-green-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        MISSING
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.after?.missing_cells ?? "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-green-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        DUPLICATES
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.after?.duplicate_rows ?? "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-green-50 p-3">
                      <p className="text-[9px] font-semibold text-gray-400">
                        COLUMNS
                      </p>
                      <p className="mt-1 text-sm font-bold text-gray-800">
                        {cleanResult.after?.columns ?? "—"}
                      </p>
                    </div>

                  </div>

                </div>

              </div>
            )}


            {/* PREVIEW */}
            {cleanResult.preview?.length > 0 && (
              <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">

                <div className="border-b border-gray-200 p-5">

                  <p className="text-xs font-bold tracking-wider text-gray-800">
                    CLEANED DATA PREVIEW
                  </p>

                  <p className="mt-1 text-xs text-gray-500">
                    Preview of the processed dataset returned by the backend.
                  </p>

                </div>

                <div className="overflow-x-auto">

                  <table className="w-full min-w-[700px] text-left">

                    <thead className="bg-gray-50">

                      <tr>

                        {Object.keys(cleanResult.preview[0]).map((column) => (
                          <th
                            key={column}
                            className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400"
                          >
                            {column}
                          </th>
                        ))}

                      </tr>

                    </thead>

                    <tbody>

                      {cleanResult.preview.slice(0, 10).map((row, rowIndex) => (

                        <tr
                          key={rowIndex}
                          className="border-t border-gray-100 hover:bg-gray-50"
                        >

                          {Object.keys(cleanResult.preview[0]).map((column) => (
                            <td
                              key={`${rowIndex}-${column}`}
                              className="whitespace-nowrap px-5 py-3 text-xs text-gray-600"
                            >
                              {row[column] === null ||
                              row[column] === undefined ||
                              row[column] === ""
                                ? "—"
                                : String(row[column])}
                            </td>
                          ))}

                        </tr>

                      ))}

                    </tbody>

                  </table>

                </div>

              </div>
            )}


            {/* CONTINUE */}
            <div className="flex justify-end">

              <button
                type="button"
                onClick={() => {
                  setActivePage("EXPLORE");
                  showToast("Cleaning completed. Ready for exploration.");
                }}
                className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-6 py-3 text-xs font-bold text-white shadow-sm transition hover:bg-red-700"
              >
                Continue to Explore
                <ChevronRight className="h-4 w-4" />
              </button>

            </div>

          </motion.div>
        )}

      </>

    )}

  </motion.div>
)}
{/* =================================================
    EXPLORE
================================================= */}
{activePage === "EXPLORE" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
    className="space-y-6"
  >
    {/* Header */}
    <div>
      <p className="text-xs font-bold tracking-wider text-red-600">
        EXPLORATORY ANALYSIS
      </p>

      <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
        Explore your dataset
      </h1>

      <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-500">
        Analyze trends, seasonality, stationarity, and
        autocorrelation before selecting forecasting models.
      </p>
    </div>

    {/* Run Analysis */}
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-900">
            Time-series analysis
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Run the statistical analysis on the active dataset.
          </p>
        </div>

        <button
          type="button"
          onClick={handleExploreDataset}
          disabled={exploreLoading || !activeDatasetId}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {exploreLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <BarChart3 className="h-4 w-4" />
              Run Analysis
            </>
          )}
        </button>
      </div>

      {!activeDatasetId && (
        <div className="mt-4 rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-700">
          Upload a dataset before running exploration.
        </div>
      )}

      {exploreError && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {exploreError}
        </div>
      )}
    </div>

    {/* Results */}
    {exploreResult && (
      <>
        {/* Dataset summary */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Observations
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {exploreResult.rows_analyzed}
            </p>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Mean
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {exploreResult.statistics?.mean ?? "—"}
            </p>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Minimum
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {exploreResult.statistics?.min ?? "—"}
            </p>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Maximum
            </p>

            <p className="mt-2 text-2xl font-bold text-gray-900">
              {exploreResult.statistics?.max ?? "—"}
            </p>
          </div>
        </div>

{/* HISTORICAL TIME SERIES */}
<div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

  <div className="flex flex-col gap-1">
    <p className="text-xs font-bold tracking-wider text-red-600">
      HISTORICAL SERIES
    </p>

    <h2 className="text-lg font-bold text-gray-900">
      Industrial production index
    </h2>

    <p className="text-sm text-gray-500">
      Historical values of the selected target variable over time.
    </p>
  </div>

  <div className="mt-6 h-[360px] w-full">
    <ResponsiveContainer
      width="100%"
      height="100%"
    >
      <RechartsLineChart
        data={exploreResult.time_series || []}
        margin={{
          top: 10,
          right: 20,
          left: 0,
          bottom: 10,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis
          dataKey="date"
          tick={{ fontSize: 10 }}
          tickMargin={8}
          minTickGap={30}
        />

        <YAxis
          tick={{ fontSize: 10 }}
          width={55}
        />

        <Tooltip
          formatter={(value) => [
            value,
            "IIP Index",
          ]}
          labelFormatter={(label) =>
            `Date: ${label}`
          }
        />

        <Line
          type="monotone"
          dataKey="value"
          name="IIP Index"
          stroke="#dc2626"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 5 }}
        />
      </RechartsLineChart>
    </ResponsiveContainer>
  </div>

</div>

{/* MONTHLY SEASONALITY */}
<div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

  <div className="flex flex-col gap-1">
    <p className="text-xs font-bold tracking-wider text-red-600">
      SEASONALITY
    </p>

    <h2 className="text-lg font-bold text-gray-900">
      Monthly seasonal pattern
    </h2>

    <p className="text-sm text-gray-500">
      Average target value for each calendar month across the available
      historical observations.
    </p>
  </div>

  <div className="mt-6 h-[340px] w-full">
    <ResponsiveContainer
      width="100%"
      height="100%"
    >
      <BarChart
        data={(exploreResult.monthly_seasonality || []).map((item) => ({
          ...item,
          month_name: new Date(2000, item.month - 1, 1).toLocaleString(
            "en-US",
            { month: "short" }
          ),
        }))}
        margin={{
          top: 10,
          right: 20,
          left: 0,
          bottom: 10,
        }}
      >

        <CartesianGrid strokeDasharray="3 3" />

        <XAxis
          dataKey="month_name"
          tick={{ fontSize: 11 }}
        />

        <YAxis
          tick={{ fontSize: 10 }}
          width={55}
        />

        <Tooltip
          formatter={(value) => [
            value,
            "Average IIP Index",
          ]}
          labelFormatter={(label) =>
            `Month: ${label}`
          }
        />

        <Bar
          dataKey="average"
          name="Average IIP Index"
          fill="#dc2626"
          radius={[5, 5, 0, 0]}
        />

      </BarChart>
    </ResponsiveContainer>
  </div>

</div>

{/* ACF + PACF */}
<div className="grid gap-6 lg:grid-cols-2">

  {/* ACF */}
  <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
    <div className="flex flex-col gap-1">
      <p className="text-xs font-bold tracking-wider text-red-600">
        AUTOCORRELATION
      </p>
      <h2 className="text-lg font-bold text-gray-900">
        ACF — Autocorrelation
      </h2>
      <p className="text-sm text-gray-500">
        Shows how strongly the series is related to its previous values at each lag.
      </p>
    </div>

    <div className="mt-5 h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={exploreResult.acf || []}
          margin={{ top: 10, right: 10, left: 0, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="lag" tick={{ fontSize: 10 }} />
          <YAxis domain={[-1, 1]} tick={{ fontSize: 10 }} width={40} />
          <Tooltip
            formatter={(value) => [Number(value).toFixed(4), "ACF"]}
            labelFormatter={(label) => `Lag: ${label}`}
          />
          <Bar dataKey="value" name="ACF" fill="#dc2626" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>

    <div className="mt-4 rounded-xl bg-gray-50 p-4 text-sm text-gray-600">
      <span className="font-semibold text-gray-900">Business meaning:</span>{" "}
      strong correlation at earlier lags can indicate that recent periods contain useful information for forecasting future demand or output.
    </div>
  </div>

  {/* PACF */}
  <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
    <div className="flex flex-col gap-1">
      <p className="text-xs font-bold tracking-wider text-red-600">
        LAG STRUCTURE
      </p>
      <h2 className="text-lg font-bold text-gray-900">
        PACF — Partial Autocorrelation
      </h2>
      <p className="text-sm text-gray-500">
        Shows the direct relationship with each lag after accounting for shorter lags.
      </p>
    </div>

    <div className="mt-5 h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={exploreResult.pacf || []}
          margin={{ top: 10, right: 10, left: 0, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="lag" tick={{ fontSize: 10 }} />
          <YAxis domain={[-1, 1]} tick={{ fontSize: 10 }} width={40} />
          <Tooltip
            formatter={(value) => [Number(value).toFixed(4), "PACF"]}
            labelFormatter={(label) => `Lag: ${label}`}
          />
          <Bar dataKey="value" name="PACF" fill="#dc2626" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>

    <div className="mt-4 rounded-xl bg-gray-50 p-4 text-sm text-gray-600">
      <span className="font-semibold text-gray-900">Modeling meaning:</span>{" "}
      PACF patterns help identify plausible autoregressive structure before statistical forecasting models are configured.
    </div>
  </div>

</div>

{/* Explore interpretation */}
<div className="rounded-2xl border border-red-100 bg-red-50/50 p-6">
  <div className="flex items-start gap-3">
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-600 text-white">
      <Sparkles className="h-4 w-4" />
    </div>
    <div>
      <p className="text-xs font-bold tracking-wider text-red-600">
        DECISION SUPPORT
      </p>
      <h2 className="mt-1 text-lg font-bold text-gray-900">
        What this analysis tells the business
      </h2>
      <p className="mt-2 text-sm leading-6 text-gray-600">
        Trend and seasonality describe the recurring planning pattern, while ACF and PACF show whether previous periods contain useful time-series structure. These findings guide the forecasting models tested in the next stage; they do not by themselves determine which model will perform best.
      </p>
    </div>
  </div>
</div>

{/* Trend and stationarity */}
<div className="grid gap-6 lg:grid-cols-2"></div>
        {/* Trend and stationarity */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-bold tracking-wider text-red-600">
              TREND
            </p>

            <h2 className="mt-2 text-xl font-bold text-gray-900">
              {exploreResult.trend?.direction ?? "—"}
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              Estimated linear trend slope:
            </p>

            <p className="mt-1 text-lg font-semibold text-gray-900">
              {exploreResult.trend?.slope ?? "—"}
            </p>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-bold tracking-wider text-red-600">
              STATIONARITY
            </p>

            <h2 className="mt-2 text-xl font-bold text-gray-900">
              ADF Test
            </h2>

            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">ADF statistic</p>
                <p className="mt-1 font-semibold text-gray-900">
                  {exploreResult.adf?.statistic ?? "—"}
                </p>
              </div>

              <div>
                <p className="text-gray-500">p-value</p>
                <p className="mt-1 font-semibold text-gray-900">
                  {exploreResult.adf?.p_value ?? "—"}
                </p>
              </div>
            </div>

            <div className="mt-4 rounded-xl bg-gray-50 p-3 text-sm">
              Original series is{" "}
              <span className="font-semibold">
                {exploreResult.adf?.stationary
                  ? "stationary"
                  : "non-stationary"}
              </span>
              .
            </div>

            <div className="mt-3 rounded-xl bg-gray-50 p-3 text-sm">
              First difference is{" "}
              <span className="font-semibold">
                {exploreResult.differenced_adf?.stationary
                  ? "stationary"
                  : "non-stationary"}
              </span>
              .
            </div>
          </div>
        </div>

        {/* Date coverage */}
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold tracking-wider text-red-600">
                DATA COVERAGE
              </p>

              <h2 className="mt-2 text-lg font-bold text-gray-900">
                Time-series coverage
              </h2>
            </div>

            <div className="text-sm text-gray-600">
              <span className="font-semibold text-gray-900">
                {exploreResult.first_date}
              </span>
              {" → "}
              <span className="font-semibold text-gray-900">
                {exploreResult.last_date}
              </span>
            </div>
          </div>
        </div>
      </>
    )}
  </motion.div>
)}
{/* =========================================================
    ANOMALIES
========================================================= */}

{activePage === "ANOMALIES" && (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="space-y-6"
  >

    {/* =====================================================
        HEADER
    ===================================================== */}

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:p-8">

      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

        <div className="flex items-start gap-4">

          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-red-50">
            <AlertTriangle className="h-6 w-6 text-red-600" />
          </div>

          <div>

            <p className="text-[10px] font-bold tracking-[0.2em] text-red-600">
              ANOMALY DETECTION
            </p>

            <h3 className="mt-1 text-xl font-bold text-gray-900">
              Detect Unusual Business Activity
            </h3>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-500">
              Identify observations that deviate significantly from
              expected historical behavior using statistical and
              machine-learning detection methods.
            </p>

          </div>

        </div>


        {/* RUN ANALYSIS */}

        <button
          type="button"
          onClick={handleAnomalyAnalysis}
          disabled={anomalyLoading || !datasetLoaded}
          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-red-600 px-5 py-3 text-xs font-bold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >

{anomalyLoading ? (
  <>
    <Loader2 className="h-4 w-4 animate-spin" />
    Analyzing...
  </>
) : (
  <>
    <AlertTriangle className="h-4 w-4" />
    {datasetLoaded
      ? "Analyse Anomalies"
      : "Upload Dataset First"}
  </>
)}

        </button>

      </div>

    </div>


    {/* =====================================================
        ERROR
    ===================================================== */}

    {anomalyError && (
      <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4">

        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />

        <div>

          <p className="text-xs font-bold text-red-700">
            Anomaly analysis failed
          </p>

          <p className="mt-1 text-xs leading-5 text-red-600">
            {anomalyError}
          </p>

        </div>

      </div>
    )}


    {/* =====================================================
        EMPTY STATE
    ===================================================== */}

    {!anomalyResult && !anomalyLoading && !anomalyError && (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-12 text-center">

        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-50">

          <AlertTriangle className="h-7 w-7 text-gray-400" />

        </div>

        <h4 className="mt-5 text-sm font-bold text-gray-800">
          No anomaly analysis loaded
        </h4>

        <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-gray-500">
          Run anomaly analysis to identify unusual observations,
          severity levels, and sector-specific patterns.
        </p>

      </div>
    )}


{/* =====================================================
    ANOMALY SUMMARY
===================================================== */}

{anomalyResult && (
  <>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">


      {/* TOTAL ANOMALIES */}

      <div className="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-red-200 hover:shadow-md">

        <div className="flex items-start justify-between">

          <div>
            <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
              TOTAL ANOMALIES
            </p>

            <p className="mt-3 text-3xl font-bold tracking-tight text-gray-900">
              {anomalyResult?.summary?.total_anomalies ?? 0}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Detected unusual observations
            </p>
          </div>

          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-red-50 transition group-hover:bg-red-100">
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>

        </div>

        <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-gray-100">
          <div className="h-full w-full rounded-full bg-red-500" />
        </div>

      </div>


      {/* HIGH SEVERITY */}

      <div className="group rounded-2xl border border-red-100 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-red-200 hover:shadow-md">

        <div className="flex items-start justify-between">

          <div>
            <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
              HIGH SEVERITY
            </p>

            <p className="mt-3 text-3xl font-bold tracking-tight text-red-600">
              {anomalyResult?.summary?.high ?? 0}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Strong deviations
            </p>
          </div>

          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-red-50 transition group-hover:bg-red-100">
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>

        </div>

        <div className="mt-4 flex items-center gap-2">

          <span className="h-2 w-2 rounded-full bg-red-500" />

          <span className="text-[11px] font-medium text-red-600">
            Requires attention
          </span>

        </div>

      </div>


      {/* MEDIUM SEVERITY */}

      <div className="group rounded-2xl border border-orange-100 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-md">

        <div className="flex items-start justify-between">

          <div>
            <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
              MEDIUM SEVERITY
            </p>

            <p className="mt-3 text-3xl font-bold tracking-tight text-orange-600">
              {anomalyResult?.summary?.medium ?? 0}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Moderate deviations
            </p>
          </div>

          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-orange-50 transition group-hover:bg-orange-100">
            <Activity className="h-5 w-5 text-orange-600" />
          </div>

        </div>

        <div className="mt-4 flex items-center gap-2">

          <span className="h-2 w-2 rounded-full bg-orange-500" />

          <span className="text-[11px] font-medium text-orange-600">
            Review historical context
          </span>

        </div>

      </div>


      {/* LOW SEVERITY */}

      <div className="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-md">

        <div className="flex items-start justify-between">

          <div>
            <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">
              LOW SEVERITY
            </p>

            <p className="mt-3 text-3xl font-bold tracking-tight text-gray-700">
              {anomalyResult?.summary?.low ?? 0}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Mild deviations
            </p>
          </div>

          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gray-100 transition group-hover:bg-gray-200">
            <Info className="h-5 w-5 text-gray-500" />
          </div>

        </div>

        <div className="mt-4 flex items-center gap-2">

          <span className="h-2 w-2 rounded-full bg-gray-400" />

          <span className="text-[11px] font-medium text-gray-500">
            Monitor as needed
          </span>

        </div>

      </div>

    </div>
  </>
)}
{/* =====================================================
    SECTOR ANOMALY SUMMARY
===================================================== */}

{anomalyResult?.sector_summary?.length > 0 && (
  <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">

    {/* HEADER */}

    <div className="flex flex-col gap-3 border-b border-gray-100 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">

      <div>

        <p className="text-xs font-bold tracking-[0.18em] text-red-600">
          SECTOR ANALYSIS
        </p>

        <h3 className="mt-1 text-lg font-bold text-gray-900">
          Anomalies by Industrial Sector
        </h3>

        <p className="mt-1 text-sm text-gray-500">
          Compare detected unusual observations across the available sectors.
        </p>

      </div>

      <div className="flex items-center gap-2 rounded-lg bg-gray-50 px-3 py-2">

        <Database className="h-4 w-4 text-gray-500" />

        <span className="text-xs font-semibold text-gray-600">
          {anomalyResult?.sector_summary?.length} sectors
        </span>

      </div>

    </div>


    {/* TABLE */}

    <div className="overflow-x-auto">

      <table className="min-w-[850px] w-full">

        <thead>

          <tr className="border-b border-gray-200 bg-gray-50">

            <th className="px-6 py-4 text-left text-[10px] font-bold tracking-[0.12em] text-gray-500">
              INDUSTRIAL SECTOR
            </th>

            <th className="px-4 py-4 text-center text-[10px] font-bold tracking-[0.12em] text-gray-500">
              OBSERVATIONS
            </th>

            <th className="px-4 py-4 text-center text-[10px] font-bold tracking-[0.12em] text-gray-500">
              STATISTICAL
            </th>

            <th className="px-4 py-4 text-center text-[10px] font-bold tracking-[0.12em] text-gray-500">
              ISOLATION FOREST
            </th>

            <th className="px-6 py-4 text-center text-[10px] font-bold tracking-[0.12em] text-gray-500">
              COMBINED
            </th>

          </tr>

        </thead>


        <tbody className="divide-y divide-gray-100">

          {anomalyResult?.sector_summary?.map((sector, index) => (

            <tr
              key={`${sector.sector}-${index}`}
              className="group transition-colors hover:bg-red-50/40"
            >

              {/* SECTOR */}

              <td className="px-6 py-4">

                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-50 text-red-600">

                    <Activity className="h-4 w-4" />

                  </div>

                  <div>

                    <p className="text-sm font-semibold text-gray-900">
                      {sector.sector}
                    </p>

                    <p className="mt-0.5 text-[11px] text-gray-400">
                      Industrial production series
                    </p>

                  </div>

                </div>

              </td>


              {/* OBSERVATIONS */}

              <td className="px-4 py-4 text-center">

                <span className="inline-flex min-w-[52px] items-center justify-center rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-bold text-gray-700">
                  {sector.observations ?? 0}
                </span>

              </td>


              {/* STATISTICAL */}

              <td className="px-4 py-4 text-center">

                <span className="inline-flex min-w-[52px] items-center justify-center rounded-lg bg-red-50 px-3 py-1.5 text-xs font-bold text-red-600">
                  {sector.statistical_anomalies ?? 0}
                </span>

              </td>


              {/* ISOLATION FOREST */}

              <td className="px-4 py-4 text-center">

                <span className="inline-flex min-w-[52px] items-center justify-center rounded-lg bg-orange-50 px-3 py-1.5 text-xs font-bold text-orange-600">
                  {sector.isolation_forest_anomalies ?? 0}
                </span>

              </td>


              {/* COMBINED */}

              <td className="px-6 py-4 text-center">

                <span className="inline-flex min-w-[58px] items-center justify-center rounded-lg bg-gray-900 px-3 py-1.5 text-xs font-bold text-white">
                  {sector.combined_anomalies ?? 0}
                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>


    {/* FOOTER */}

    <div className="border-t border-gray-100 bg-gray-50 px-6 py-3">

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[11px] text-gray-500">

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-red-500" />
          Statistical detection
        </div>

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-orange-500" />
          Isolation Forest
        </div>

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-gray-800" />
          Combined detection
        </div>

      </div>

    </div>

  </div>
)}

        {anomalyResult && (
          <>
            {/* =================================================
                ANOMALY VISUAL ANALYSIS
            ================================================= */}

            <div className="grid gap-6 xl:grid-cols-2">

          {/* =================================================
              SECTOR ANOMALY COMPARISON
          ================================================= */}

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

            <div className="mb-5">

              <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
                SECTOR COMPARISON
              </p>

              <h4 className="mt-1 text-lg font-bold text-gray-900">
                Anomalies by Sector
              </h4>

              <p className="mt-1 text-xs text-gray-500">
                Combined anomaly detections across industrial sectors.
              </p>

            </div>

            <div className="h-[300px] w-full">

              <ResponsiveContainer width="100%" height="100%">

                <BarChart
                data={anomalyResult?.sector_summary || []}
                  margin={{
                    top: 10,
                    right: 10,
                    left: 0,
                    bottom: 10,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="sector"
                    tick={{
                      fontSize: 9,
                    }}
                    angle={-20}
                    textAnchor="end"
                    height={65}
                    interval={0}
                  />

                  <YAxis
                    allowDecimals={false}
                    tick={{
                      fontSize: 10,
                    }}
                  />

                  <Tooltip
                    contentStyle={{
                      borderRadius: "10px",
                      border: "1px solid #e5e7eb",
                      fontSize: "11px",
                    }}
                  />

                  <Bar
                    dataKey="combined_anomalies"
                    name="Combined anomalies"
                    fill="#dc2626"
                    radius={[5, 5, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>


          {/* =================================================
              SEVERITY DISTRIBUTION
          ================================================= */}

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

            <div className="mb-5">

              <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
                SEVERITY DISTRIBUTION
              </p>

              <h4 className="mt-1 text-lg font-bold text-gray-900">
                Anomaly Severity
              </h4>

              <p className="mt-1 text-xs text-gray-500">
                Distribution of detected observations by deviation level.
              </p>

            </div>

            <div className="h-[300px] w-full">

              <ResponsiveContainer width="100%" height="100%">

                <BarChart
                  data={[
                    {
                      severity: "High",
                      count: anomalyResult?.summary?.high ?? 0,
                    },
                    {
                      severity: "Medium",
                      count: anomalyResult?.summary?.medium ?? 0,
                    },
                    {
                      severity: "Low",
                    count: anomalyResult?.summary?.low ?? 0,
                    },
                  ]}
                  margin={{
                    top: 10,
                    right: 10,
                    left: 0,
                    bottom: 10,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="severity"
                    tick={{
                      fontSize: 10,
                    }}
                  />

                  <YAxis
                    allowDecimals={false}
                    tick={{
                      fontSize: 10,
                    }}
                  />

                  <Tooltip
                    contentStyle={{
                      borderRadius: "10px",
                      border: "1px solid #e5e7eb",
                      fontSize: "11px",
                    }}
                  />

                  <Bar
                    dataKey="count"
                    name="Anomalies"
                    fill="#ef4444"
                    radius={[5, 5, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>


          {/* =================================================
              ANOMALY VALUE TIMELINE
          ================================================= */}

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm xl:col-span-2">

            <div className="mb-5">

              <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
                ANOMALY TIMELINE
              </p>

              <h4 className="mt-1 text-lg font-bold text-gray-900">
                Detected Values Over Time
              </h4>

              <p className="mt-1 text-xs text-gray-500">
                Historical values associated with detected anomalies.
              </p>

            </div>

            <div className="h-[340px] w-full">

              <ResponsiveContainer width="100%" height="100%">

                <RechartsLineChart
                  data={anomalyResult?.timeline || []}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="date"
                    tick={{
                      fontSize: 9,
                    }}
                    minTickGap={35}
                  />

                  <YAxis
                    tick={{
                      fontSize: 10,
                    }}
                  />

                  <Tooltip
                    contentStyle={{
                      borderRadius: "10px",
                      border: "1px solid #e5e7eb",
                      fontSize: "11px",
                    }}
                    formatter={(value, name) => [
                      typeof value === "number"
                        ? value.toFixed(2)
                        : value,
                      name === "value"
                        ? "Observed value"
                        : name,
                    ]}
                  />

                  <Line
                    type="monotone"
                    dataKey="value"
                    name="value"
                    stroke="#dc2626"
                    strokeWidth={2}
                    dot={{
                      r: 3,
                    }}
                    activeDot={{
                      r: 6,
                    }}
                  />

                </RechartsLineChart>

              </ResponsiveContainer>

            </div>

          </div>


          {/* =================================================
              RESIDUAL / DEVIATION CHART
          ================================================= */}

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm xl:col-span-2">

            <div className="mb-5">

              <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
                DEVIATION ANALYSIS
              </p>

              <h4 className="mt-1 text-lg font-bold text-gray-900">
                Residual Magnitude
              </h4>

              <p className="mt-1 text-xs text-gray-500">
                Positive values indicate observations above expected behavior;
                negative values indicate observations below expected behavior.
              </p>

            </div>

            <div className="h-[320px] w-full">

              <ResponsiveContainer width="100%" height="100%">

                <BarChart
                  data={anomalyResult?.timeline || []}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="date"
                    tick={{
                      fontSize: 9,
                    }}
                    minTickGap={35}
                  />

                  <YAxis
                    tick={{
                      fontSize: 10,
                    }}
                  />

                  <Tooltip
                    contentStyle={{
                      borderRadius: "10px",
                      border: "1px solid #e5e7eb",
                      fontSize: "11px",
                    }}
                    formatter={(value) => [
                      typeof value === "number"
                        ? value.toFixed(2)
                        : value,
                      "Residual",
                    ]}
                  />

                  <Bar
                    dataKey="residual"
                    name="Residual"
                    fill="#dc2626"
                    radius={[3, 3, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>

        </div>
        {/* =================================================
            ANOMALY TIMELINE
        ================================================= */}

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="mb-5">

            <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
              ANOMALY TIMELINE
            </p>

            <h4 className="mt-1 text-lg font-bold text-gray-900">
              Detected Unusual Observations
            </h4>

            <p className="mt-1 text-xs text-gray-500">
              Historical observations flagged by the anomaly detection pipeline.
            </p>

          </div>


          <div className="max-h-[520px] overflow-auto rounded-xl border border-gray-200">

            <table className="w-full min-w-[900px] text-left">

              <thead className="sticky top-0 bg-gray-50">

                <tr className="border-b border-gray-200">

                  <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                    DATE
                  </th>

                  <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                    SECTOR
                  </th>

                  <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                    VALUE
                  </th>

                  <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                    RESIDUAL
                  </th>

                  <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                    ROBUST Z
                  </th>

                  <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                    SEVERITY
                  </th>

                  <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                    DIRECTION
                  </th>

                </tr>

              </thead>


              <tbody>

                {(anomalyResult?.timeline || []).map(
                  (item, index) => (

                    <tr
                      key={`${item.date}-${item.sector}-${index}`}
                      className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                    >

                      <td className="px-4 py-3 text-xs font-medium text-gray-700">
                        {item.date}
                      </td>

                      <td className="px-4 py-3 text-xs font-semibold text-gray-800">
                        {item.sector}
                      </td>

                      <td className="px-4 py-3 text-xs text-gray-600">
                        {item.value?.toFixed?.(2) ?? "—"}
                      </td>

                      <td className="px-4 py-3 text-xs text-gray-600">
                        {item.residual?.toFixed?.(2) ?? "—"}
                      </td>

                      <td className="px-4 py-3 text-xs font-semibold text-gray-700">
                        {item.robust_z_score?.toFixed?.(2) ?? "—"}
                      </td>

                      <td className="px-4 py-3">

                        <span
                          className={`inline-flex rounded-full px-2.5 py-1 text-[10px] font-bold ${
                            item.severity === "HIGH"
                              ? "bg-red-100 text-red-700"
                              : item.severity === "MEDIUM"
                              ? "bg-orange-100 text-orange-700"
                              : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {item.severity}
                        </span>

                      </td>

                      <td className="px-4 py-3 text-xs font-medium text-gray-600">
                        {item.direction}
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        </div>
                {/* =================================================
            STRUCTURAL BREAKS
        ================================================= */}

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

            <div>

              <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
                STRUCTURAL CHANGE DETECTION
              </p>

              <h4 className="mt-1 text-lg font-bold text-gray-900">
                Structural Breaks by Sector
              </h4>

              <p className="mt-1 max-w-2xl text-xs leading-5 text-gray-500">
                Detected points where the statistical behavior of a sector
                changed materially rather than representing only an isolated
                unusual observation.
              </p>

            </div>

            <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3">

              <p className="text-[9px] font-bold tracking-wider text-gray-400">
                DETECTION METHOD
              </p>

              <p className="mt-1 text-xs font-bold text-gray-700">
                Pettitt Test
              </p>

            </div>

          </div>


          {/* STRUCTURAL BREAK CARDS */}

          <div className="mt-6 grid gap-4 md:grid-cols-2">

            {(anomalyResult?.structural_breaks || []).map((item) => (

              <div
                key={item.sector}
                className="rounded-xl border border-gray-200 bg-gray-50 p-5 transition hover:border-red-200 hover:bg-red-50/30"
              >

                <div className="flex items-start justify-between gap-4">

                  <div>

                    <p className="text-sm font-bold text-gray-900">
                      {item.sector}
                    </p>

                    <p className="mt-1 text-xs text-gray-500">
                      Break detected: {item.date}
                    </p>

                  </div>

                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white">
                    <Activity className="h-4 w-4 text-red-600" />
                  </div>

                </div>


                <div className="mt-5 grid grid-cols-2 gap-3">

                  <div className="rounded-lg border border-gray-200 bg-white p-3">

                    <p className="text-[9px] font-bold tracking-wider text-gray-400">
                      MEAN CHANGE
                    </p>

                    <p
                      className={`mt-1 text-lg font-bold ${
                        Number(item.change) < 0
                          ? "text-red-600"
                          : "text-green-600"
                      }`}
                    >
                      {item.change}
                    </p>

                  </div>


                  <div className="rounded-lg border border-gray-200 bg-white p-3">

                    <p className="text-[9px] font-bold tracking-wider text-gray-400">
                      DIRECTION
                    </p>

                    <p className="mt-1 text-sm font-bold text-gray-800">
                      {item.direction}
                    </p>

                  </div>

                </div>

              </div>

            ))}

          </div>


          {/* INTERPRETATION */}

          <div className="mt-5 rounded-xl border border-gray-200 bg-white p-5">

            <div className="flex items-start gap-3">

              <Info className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />

              <div>

                <p className="text-xs font-bold text-gray-800">
                  How to interpret a structural break
                </p>

                <p className="mt-1 text-xs leading-5 text-gray-500">
                  A structural break indicates a sustained change in the
                  statistical behavior of the series. It should not
                  automatically be interpreted as a single-month anomaly
                  or as evidence of a specific causal event.
                </p>

              </div>

            </div>

          </div>
        </div>

          </>
        )}

  </motion.div>
)}


{/* =================================================
    MODELS
================================================= */}

{activePage === "MODELS" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
    className="space-y-6"
  >
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <p className="text-xs font-bold tracking-[0.18em] text-red-600">
        FORECASTING MODEL LAB
      </p>
      <h1 className="mt-2 text-3xl font-bold text-gray-900">
        Forecasting Models
      </h1>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-500">
        Run statistical, machine-learning, and deep-learning forecasting
        models on the active time series. Each model returns its forecast,
        configuration, and model-specific parameters.
      </p>
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-bold text-gray-900">
          Select Forecasting Model
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Select one model. The configuration and results below update automatically.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            id: "tesm",
            name: "TESM / Holt-Winters",
            description: "Level, trend, and seasonal components",
          },
          {
            id: "sarima",
            name: "SARIMA",
            description: "Autoregressive seasonal time-series model",
          },
          {
            id: "sarimax",
            name: "SARIMAX",
            description: "SARIMA with an external regressor",
          },
          {
            id: "random_forest",
            name: "Random Forest",
            description: "Recursive lag-feature regression",
          },
          {
            id: "xgboost",
            name: "XGBoost",
            description: "Gradient-boosted lag-feature regression",
          },
          {
            id: "lstm",
            name: "LSTM",
            description: "Long short-term memory sequence model",
          },
          {
            id: "gru",
            name: "GRU",
            description: "Gated recurrent sequence model",
          },
        ].map((model) => (
          <button
            key={model.id}
            type="button"
            onClick={() => {
              setSelectedModel(model.id);
              setModelResult(null);
              setModelError("");
            }}
            className={`rounded-xl border p-5 text-left transition ${
              selectedModel === model.id
                ? "border-red-500 bg-red-50 shadow-sm"
                : "border-gray-200 bg-white hover:border-red-300 hover:bg-gray-50"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold text-gray-900">{model.name}</h3>
                <p className="mt-2 text-xs leading-5 text-gray-500">
                  {model.description}
                </p>
              </div>

              {selectedModel === model.id && (
                <span className="shrink-0 rounded-full bg-red-600 px-2 py-1 text-[10px] font-bold text-white">
                  SELECTED
                </span>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-6">
        <p className="text-xs font-bold tracking-[0.18em] text-red-600">
          MODEL CONFIGURATION
        </p>
        <h2 className="mt-2 text-xl font-bold text-gray-900">
          {getModelDisplayName(selectedModel)}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Configure the forecast horizon and model-specific inputs.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        <div>
          <label className="mb-2 block text-sm font-semibold text-gray-700">
            Date Column
          </label>
          <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700">
            {dateColumn || "Not selected"}
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-gray-700">
            Target Column
          </label>
          <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700">
            {targetColumn || "Not selected"}
          </div>
        </div>

        <div>
          <label
            htmlFor="model-forecast-horizon"
            className="mb-2 block text-sm font-semibold text-gray-700"
          >
            Forecast Horizon
          </label>
          <select
            id="model-forecast-horizon"
            value={forecastHorizon}
            onChange={(event) =>
              setForecastHorizon(Number(event.target.value))
            }
            className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 outline-none focus:border-red-500 focus:ring-2 focus:ring-red-100"
          >
            <option value={3}>3 months</option>
            <option value={6}>6 months</option>
            <option value={12}>12 months</option>
            <option value={18}>18 months</option>
            <option value={24}>24 months</option>
          </select>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
          <p className="text-[10px] font-bold tracking-wider text-gray-400">
            MODEL
          </p>
          <p className="mt-2 text-sm font-bold text-gray-900">
            {getModelDisplayName(selectedModel)}
          </p>
          <p className="mt-1 text-xs leading-5 text-gray-500">
            {selectedModel === "tesm"
              ? "Additive trend and additive seasonality with period 12."
              : selectedModel === "sarima"
                ? "SARIMA(1,1,1)(1,1,1)[12]."
                : selectedModel === "sarimax"
                  ? "SARIMA with an external regressor."
                  : selectedModel === "random_forest"
                    ? "Recursive lag and rolling-feature regression."
                    : selectedModel === "xgboost"
                      ? "Recursive gradient boosting on time-series features."
                      : selectedModel === "lstm"
                        ? "Sequence model using the previous 12 observations."
                        : "GRU sequence model using the previous 12 observations."}
          </p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
          <p className="text-[10px] font-bold tracking-wider text-gray-400">
            ACTIVE DATASET
          </p>
          <p className="mt-2 text-sm font-bold text-gray-900">
            {datasetLoaded ? selectedFile?.name : "No dataset loaded"}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            {datasetLoaded
              ? `${quality.rows.toLocaleString()} observations · target: ${targetColumn}`
              : "Upload and prepare a dataset first."}
          </p>
        </div>
      </div>

      {selectedModel === "sarimax" && (
        <div className="mt-5 rounded-xl border border-red-100 bg-red-50 p-5">
          <label
            htmlFor="sarimax-exog-column"
            className="block text-sm font-bold text-gray-800"
          >
            External Variable
          </label>
          <p className="mt-1 text-xs leading-5 text-gray-600">
            Choose a numeric external variable from the uploaded dataset, or
            leave automatic to use the project's available CPI series when it
            matches the target dates.
          </p>
          <select
            id="sarimax-exog-column"
            value={modelConfig.exog_column}
            onChange={(event) =>
              setModelConfig((current) => ({
                ...current,
                exog_column: event.target.value,
              }))
            }
            className="mt-4 w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 outline-none focus:border-red-500 focus:ring-2 focus:ring-red-100"
          >
            <option value="">Automatic external variable</option>
            {(datasetProfile?.numeric_columns || [])
              .filter(
                (column) =>
                  column !== targetColumn &&
                  !["year", "month"].includes(
                    String(column).trim().toLowerCase()
                  )
              )
              .map((column) => (
                <option key={column} value={column}>
                  {column}
                </option>
              ))}
          </select>
        </div>
      )}

      <div className="mt-6 flex flex-wrap justify-end gap-3">
        <button
          type="button"
          onClick={handleAllModelsForecast}
          disabled={modelLoading || !datasetLoaded}
          className="inline-flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-6 py-3 text-sm font-semibold text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {modelLoading ? "Running Models..." : "Run All Models"}
        </button>

        <button
          type="button"
          onClick={handleSelectedModelForecast}
          disabled={modelLoading || !datasetLoaded}
          className="inline-flex items-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {modelLoading
            ? `Running ${getModelDisplayName(selectedModel)}...`
            : `Run ${getModelDisplayName(selectedModel)} Forecast`}
        </button>
      </div>

      {modelError && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {modelError}
        </div>
      )}
    </div>

    {unifiedModelComparison.length > 0 && (
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-6">
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            MODEL COMPARISON
          </p>
          <h2 className="mt-2 text-xl font-bold text-gray-900">
            Unified Forecasting Results
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Live unified forecasts are combined with the dataset-specific walk-forward and final-test validation metrics.
          </p>
        </div>

        <div className="mb-5 rounded-xl border border-gray-200 bg-gray-50 p-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Walk-Forward
              </p>
              <p className="mt-1 text-sm font-medium text-gray-900">
                {validationResult?.methodology?.walk_forward_origins?.length || 0} rolling origins
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Final Test
              </p>
              <p className="mt-1 text-sm font-medium text-gray-900">
                {validationResult?.methodology?.test_period ||
                  validationResult?.methodology?.final_test_period ||
                  "Chronological holdout"}
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Forecast Horizon
              </p>
              <p className="mt-1 text-sm font-medium text-gray-900">
                {forecastHorizon} months
              </p>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                {['Model','WF MAE','WF RMSE','WF MAPE','Final MAE','Final RMSE','Final MAPE','AIC','BIC','Forecast Points'].map((heading) => (
                  <th key={heading} className="px-4 py-3 font-semibold text-gray-600">
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {unifiedModelComparison.map((model) => (
                <tr key={model.key} className="border-b border-gray-100">
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {model.name}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.walkForwardMae !== null ? model.walkForwardMae.toFixed(3) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.walkForwardRmse !== null ? model.walkForwardRmse.toFixed(3) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.walkForwardMape !== null ? `${model.walkForwardMape.toFixed(3)}%` : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.finalTestMae !== null ? model.finalTestMae.toFixed(3) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.finalTestRmse !== null ? model.finalTestRmse.toFixed(3) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.finalTestMape !== null ? `${model.finalTestMape.toFixed(3)}%` : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.aic !== null ? model.aic.toFixed(3) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.bic !== null ? model.bic.toFixed(3) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {model.forecastCount || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-4 text-xs leading-5 text-gray-500">
          SARIMAX remains in the validation comparison when validation data is available; the Run All Models batch intentionally uses the six-model unified request because the current unified SARIMAX contract requires an explicit external-variable column.
        </p>
      </div>
    )}

    {modelResult && (
      <div className="space-y-6">
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-red-600">
                FORECAST COMPLETED
              </p>
              <h3 className="mt-1 text-xl font-bold text-gray-900">
                {modelResult.model?.name || getModelDisplayName(selectedModel)}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {modelResult.forecast?.length || 0}-period forecast generated
                from the selected dataset.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <div className="rounded-xl bg-gray-50 px-4 py-3">
                <p className="text-[9px] font-bold tracking-wider text-gray-400">
                  OBSERVATIONS
                </p>
                <p className="mt-1 text-sm font-bold text-gray-900">
                  {modelResult.model?.observations ?? "—"}
                </p>
              </div>

              <div className="rounded-xl bg-gray-50 px-4 py-3">
                <p className="text-[9px] font-bold tracking-wider text-gray-400">
                  HORIZON
                </p>
                <p className="mt-1 text-sm font-bold text-gray-900">
                  {modelResult.model?.horizon ?? "—"}
                </p>
              </div>

              {modelResult.model?.aic !== undefined && (
                <div className="rounded-xl bg-gray-50 px-4 py-3">
                  <p className="text-[9px] font-bold tracking-wider text-gray-400">
                    AIC
                  </p>
                  <p className="mt-1 text-sm font-bold text-gray-900">
                    {Number(modelResult.model.aic).toFixed(3)}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {modelChartData.length > 0 && (
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-xs font-bold uppercase tracking-wider text-red-600">
                FORECAST VISUALIZATION
              </p>
              <h3 className="mt-1 text-lg font-bold text-gray-900">
                Historical vs {modelResult.model?.name || "Model"} Forecast
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Historical observations followed by the model forecast.
                Prediction intervals appear when the model supplies them.
              </p>
            </div>

            <div className="h-[400px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsLineChart
                  data={modelChartData}
                  margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 10 }}
                    tickMargin={8}
                    minTickGap={30}
                  />
                  <YAxis tick={{ fontSize: 10 }} width={55} />
                  <Tooltip
                    formatter={(value, name) => [
                      value !== null && value !== undefined
                        ? Number(value).toFixed(2)
                        : "-",
                      name,
                    ]}
                    labelFormatter={(label) => `Date: ${label}`}
                  />

                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Historical"
                    stroke="#374151"
                    strokeWidth={2}
                    dot={false}
                    connectNulls={false}
                  />

                  <Line
                    type="monotone"
                    dataKey="forecast"
                    name={`${modelResult.model?.name || "Model"} Forecast`}
                    stroke="#dc2626"
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    connectNulls={false}
                  />

                  {modelChartData.some(
                    (item) => item.lower !== null && item.upper !== null
                  ) && (
                    <>
                      <Line
                        type="monotone"
                        dataKey="lower"
                        name="Lower 95% Bound"
                        stroke="#9ca3af"
                        strokeWidth={1.5}
                        strokeDasharray="5 5"
                        dot={false}
                        connectNulls={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="upper"
                        name="Upper 95% Bound"
                        stroke="#9ca3af"
                        strokeWidth={1.5}
                        strokeDasharray="5 5"
                        dot={false}
                        connectNulls={false}
                      />
                    </>
                  )}
                </RechartsLineChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 flex flex-wrap gap-5 text-xs font-medium text-gray-600">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-7 rounded-full bg-gray-700" />
                Historical
              </div>
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-7 rounded-full bg-red-600" />
                Forecast
              </div>
              {modelChartData.some(
                (item) => item.lower !== null && item.upper !== null
              ) && (
                <div className="flex items-center gap-2">
                  <span className="h-0 w-7 border-t-2 border-dashed border-gray-400" />
                  95% prediction interval
                </div>
              )}
            </div>
          </div>
        )}

        {modelResult.model && (
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
              <p className="text-xs font-bold uppercase tracking-wider text-red-600">
                MODEL PARAMETERS
              </p>
              <h3 className="mt-1 text-lg font-bold text-gray-900">
                Configuration and estimated parameters
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                These values describe the model that was actually fitted.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(
                modelResult.model.parameters ||
                  modelResult.parameters ||
                  Object.fromEntries(
                    Object.entries(modelResult.model).filter(
                      ([key]) =>
                        ![
                          "name",
                          "type",
                          "observations",
                          "horizon",
                        ].includes(key)
                    )
                  )
              ).map(([key, value]) => (
                <div
                  key={key}
                  className="rounded-xl border border-gray-200 bg-gray-50 p-4"
                >
                  <p className="text-[9px] font-bold uppercase tracking-wider text-gray-400">
                    {String(key).replaceAll("_", " ")}
                  </p>
                  <p className="mt-2 break-words text-sm font-bold text-gray-900">
                    {typeof value === "number"
                      ? Number(value).toFixed(4)
                      : String(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {modelResult.forecast?.length > 0 && (
          <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
            <div className="border-b border-gray-100 px-6 py-4">
              <p className="text-xs font-bold uppercase tracking-wider text-red-600">
                FORECAST VALUES
              </p>
              <h3 className="mt-1 text-base font-bold text-gray-900">
                Future forecast
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Point forecast and prediction interval where available.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
<th className="px-6 py-3 text-left font-semibold text-gray-600">
  Period
</th>

<th className="px-6 py-3 text-right font-semibold text-gray-600">
  Forecast
</th>

<th className="px-6 py-3 text-right font-semibold text-gray-600">
  Lower Bound
</th>

<th className="px-6 py-3 text-right font-semibold text-gray-600">
  Upper Bound
</th>

<th className="px-6 py-3 text-right font-semibold text-gray-600">
  Interval Width
</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-gray-100">
                  {modelResult.forecast.map((item, index) => (
                    <tr
                      key={`${item.date}-${index}`}
                      className="transition hover:bg-red-50/40"
                    >
                      <td className="px-6 py-3 font-medium text-gray-800">
                        {item.date}
                      </td>
                      <td className="px-6 py-3 text-right font-semibold text-red-600">
                        {Number(item.value).toFixed(2)}
                      </td>
                      <td className="px-6 py-3 text-right text-gray-600">
                        {item.lower !== undefined && item.lower !== null
                          ? Number(item.lower).toFixed(2)
                          : "—"}
                      </td>
                      <td className="px-6 py-3 text-right text-gray-600">
                        {item.upper !== undefined && item.upper !== null
                          ? Number(item.upper).toFixed(2)
                          : "—"}
                      </td>
                            {/* INTERVAL WIDTH */}

      <td className="px-6 py-3 text-right text-gray-600">
        {item.lower !== undefined &&
        item.lower !== null &&
        item.upper !== undefined &&
        item.upper !== null
          ? (
              Number(item.upper) - Number(item.lower)
            ).toFixed(2)
          : "—"}
      </td>

                    </tr>
                  ))}

                </tbody>
              </table>
            </div>
          </div>
        )}

        {modelResult.metrics &&
          Object.keys(modelResult.metrics).length > 0 && (
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-bold uppercase tracking-wider text-red-600">
                MODEL METRICS
              </p>
              <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {Object.entries(modelResult.metrics).map(([key, value]) => (
                  <div key={key} className="rounded-xl bg-gray-50 p-4">
                    <p className="text-[9px] font-bold uppercase tracking-wider text-gray-400">
                      {key.replaceAll("_", " ")}
                    </p>
                    <p className="mt-2 text-xl font-bold text-gray-900">
                      {typeof value === "number"
                        ? Number(value).toFixed(4)
                        : String(value)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
      </div>
    )}
  </motion.div>
)}
{/* =================================================
    VALIDATE
================================================= */}

{activePage === "VALIDATE" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
    className="space-y-6"
  >

    {/* HEADER */}

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

        <div>
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            MODEL VALIDATION
          </p>

          <h2 className="mt-2 text-2xl font-bold text-gray-900">
            Measure Forecast Reliability
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-500">
            Evaluate forecasting performance using chronological
            walk-forward validation and a separate final test period.
          </p>
        </div>

        <button
          type="button"
          onClick={handleValidation}
          disabled={validationLoading}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {validationLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading...
            </>
          ) : (
            <>
              <Gauge className="h-4 w-4" />
              Run Validation
            </>
          )}
        </button>

      </div>
    </div>

    {/* ERROR */}

    {validationError && (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">

        <div className="flex items-start gap-3">

          <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

          <div>
            <p className="text-sm font-semibold text-red-800">
              Validation error
            </p>

            <p className="mt-1 text-xs leading-5 text-red-700">
              {validationError}
            </p>
          </div>

        </div>

      </div>
    )}

    {/* EMPTY STATE */}

    {!validationResult && !validationLoading && !validationError && (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center shadow-sm">

        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-600">
          <Gauge className="h-7 w-7" />
        </div>

        <h3 className="mt-4 text-lg font-bold text-gray-900">
          Validation results are ready
        </h3>

        <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-gray-500">
          Run validation to load the completed walk-forward and
          final-test performance results.
        </p>

        <button
          type="button"
          onClick={handleValidation}
          className="mt-5 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-red-700"
        >
          Load Validation Results
        </button>

      </div>
    )}

    {/* RESULTS */}

    {validationResult && (
      <>

        {/* METHODOLOGY */}

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="flex items-start gap-3">

            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-50 text-red-600">
              <ShieldCheck className="h-5 w-5" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-gray-900">
                Validation Methodology
              </h3>

              <p className="mt-1 text-sm leading-6 text-gray-500">
                {validationResult.methodology?.description}
              </p>
            </div>

          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
              <p className="text-[10px] font-bold tracking-wider text-gray-400">
                METHOD
              </p>
              <p className="mt-2 text-sm font-semibold text-gray-900">
                Walk-forward
              </p>
            </div>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
              <p className="text-[10px] font-bold tracking-wider text-gray-400">
                FREQUENCY
              </p>
              <p className="mt-2 text-sm font-semibold text-gray-900">
                {validationResult.methodology?.frequency}
              </p>
            </div>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
              <p className="text-[10px] font-bold tracking-wider text-gray-400">
                HORIZON
              </p>
              <p className="mt-2 text-sm font-semibold text-gray-900">
                {validationResult.methodology?.forecast_horizon} months
              </p>
            </div>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
              <p className="text-[10px] font-bold tracking-wider text-gray-400">
                FINAL TEST
              </p>
              <p className="mt-2 text-sm font-semibold text-gray-900">
                {validationResult.methodology?.final_test_observations} months
              </p>
            </div>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
              <p className="text-[10px] font-bold tracking-wider text-gray-400">
                SHUFFLING
              </p>
              <p className="mt-2 text-sm font-semibold text-gray-900">
                No
              </p>
            </div>

          </div>

        </div>

        {/* WALK-FORWARD */}

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="mb-5">
            <p className="text-xs font-bold tracking-[0.18em] text-red-600">
              WALK-FORWARD VALIDATION
            </p>

            <h3 className="mt-2 text-xl font-bold text-gray-900">
              Historical Performance
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Average performance across the completed chronological
              validation periods.
            </p>
          </div>

          <div className="overflow-x-auto">

            <table className="w-full min-w-[760px] text-left">

              <thead>
                <tr className="border-b border-gray-200">

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    MODEL
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    MAE
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    RMSE
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    MAPE
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    AIC
                  </th>

                </tr>
              </thead>

              <tbody>

                {validationResult.walk_forward?.map((item) => (
                  <tr
                    key={`${item.model}-${item.variant}`}
                    className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                  >

                    <td className="px-4 py-4">

                      <p className="text-sm font-semibold text-gray-900">
                        {item.model}
                      </p>

                      <p className="mt-1 text-xs text-gray-400">
                        {item.variant}
                      </p>

                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {Number(item.mae).toFixed(3)}
                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {Number(item.rmse).toFixed(3)}
                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {Number(item.mape).toFixed(3)}%
                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {item.aic !== null && item.aic !== undefined
                        ? Number(item.aic).toFixed(3)
                        : "N/A"}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </div>

        {/* FINAL TEST */}

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="mb-5">

            <p className="text-xs font-bold tracking-[0.18em] text-red-600">
              FINAL UNTOUCHED TEST
            </p>

            <h3 className="mt-2 text-xl font-bold text-gray-900">
              Final Test Performance
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Performance on the 12-month final test period:
              April 2024 to March 2025.
            </p>

          </div>

          <div className="overflow-x-auto">

            <table className="w-full min-w-[760px] text-left">

              <thead>

                <tr className="border-b border-gray-200">

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    MODEL
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    MAE
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    RMSE
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    MAPE
                  </th>

                  <th className="px-4 py-3 text-xs font-bold text-gray-500">
                    AIC
                  </th>

                </tr>

              </thead>

              <tbody>

                {validationResult.final_test?.map((item) => (
                  <tr
                    key={item.model}
                    className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                  >

                    <td className="px-4 py-4">

                      <p className="text-sm font-semibold text-gray-900">
                        {item.model}
                      </p>

                      {item.note && (
                        <p className="mt-1 max-w-md text-[11px] leading-4 text-amber-600">
                          {item.note}
                        </p>
                      )}

                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {Number(item.mae).toFixed(3)}
                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {Number(item.rmse).toFixed(3)}
                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {Number(item.mape).toFixed(3)}%
                    </td>

                    <td className="px-4 py-4 text-sm text-gray-700">
                      {item.aic !== null && item.aic !== undefined
                        ? Number(item.aic).toFixed(3)
                        : "N/A"}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </div>
{/* =================================================
    VALIDATION CHARTS
================================================= */}

<div className="space-y-6">

  {/* CHART SECTION HEADER */}

  <div>
    <p className="text-xs font-bold tracking-[0.18em] text-red-600">
      VISUAL PERFORMANCE ANALYSIS
    </p>

    <h3 className="mt-2 text-xl font-bold text-gray-900">
      Forecast Error Comparison
    </h3>

    <p className="mt-1 text-sm text-gray-500">
      Compare forecast error across models. Lower MAE, RMSE, and MAPE
      indicate lower historical prediction error for the evaluated period.
    </p>
  </div>


  {/* =================================================
      MAE
  ================================================= */}

  <div className="grid gap-6 xl:grid-cols-2">

    {/* WALK-FORWARD MAE */}

    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

      <div className="mb-4">
        <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
          WALK-FORWARD
        </p>

        <h4 className="mt-1 text-base font-bold text-gray-900">
          MAE Comparison
        </h4>

        <p className="mt-1 text-xs text-gray-500">
          Mean Absolute Error across historical validation periods.
        </p>
      </div>

      <div className="h-[300px] w-full">

        <ResponsiveContainer width="100%" height="100%">

          <BarChart
            layout="vertical"
            data={(validationResult.walk_forward || []).map((item) => ({
              model: item.model,
              mae: Number(item.mae),
            }))}
            margin={{
              top: 5,
              right: 20,
              left: 20,
              bottom: 5,
            }}
          >

            <CartesianGrid strokeDasharray="3 3" horizontal={false} />

            <XAxis
              type="number"
              tick={{ fontSize: 10 }}
            />

            <YAxis
              type="category"
              dataKey="model"
              width={95}
              tick={{ fontSize: 9 }}
            />

            <Tooltip
              formatter={(value) => [
                Number(value).toFixed(3),
                "MAE",
              ]}
            />

            <Bar
              dataKey="mae"
              fill="#dc2626"
              radius={[0, 4, 4, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>


    {/* FINAL TEST MAE */}

    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

      <div className="mb-4">
        <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
          FINAL TEST
        </p>

        <h4 className="mt-1 text-base font-bold text-gray-900">
          MAE Comparison
        </h4>

        <p className="mt-1 text-xs text-gray-500">
          Error on the final April 2024 – March 2025 test period.
        </p>
      </div>

      <div className="h-[300px] w-full">

        <ResponsiveContainer width="100%" height="100%">

          <BarChart
            layout="vertical"
            data={(validationResult.final_test || []).map((item) => ({
              model: item.model,
              mae: Number(item.mae),
            }))}
            margin={{
              top: 5,
              right: 20,
              left: 20,
              bottom: 5,
            }}
          >

            <CartesianGrid strokeDasharray="3 3" horizontal={false} />

            <XAxis
              type="number"
              tick={{ fontSize: 10 }}
            />

            <YAxis
              type="category"
              dataKey="model"
              width={95}
              tick={{ fontSize: 9 }}
            />

            <Tooltip
              formatter={(value) => [
                Number(value).toFixed(3),
                "MAE",
              ]}
            />

            <Bar
              dataKey="mae"
              fill="#dc2626"
              radius={[0, 4, 4, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>

  </div>


  {/* =================================================
      RMSE
  ================================================= */}

  <div className="grid gap-6 xl:grid-cols-2">

    {/* WALK-FORWARD RMSE */}

    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

      <div className="mb-4">
        <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
          WALK-FORWARD
        </p>

        <h4 className="mt-1 text-base font-bold text-gray-900">
          RMSE Comparison
        </h4>

        <p className="mt-1 text-xs text-gray-500">
          Root Mean Squared Error, which gives greater weight to larger errors.
        </p>
      </div>

      <div className="h-[300px] w-full">

        <ResponsiveContainer width="100%" height="100%">

          <BarChart
            layout="vertical"
            data={(validationResult.walk_forward || []).map((item) => ({
              model: item.model,
              rmse: Number(item.rmse),
            }))}
            margin={{
              top: 5,
              right: 20,
              left: 20,
              bottom: 5,
            }}
          >

            <CartesianGrid strokeDasharray="3 3" horizontal={false} />

            <XAxis
              type="number"
              tick={{ fontSize: 10 }}
            />

            <YAxis
              type="category"
              dataKey="model"
              width={95}
              tick={{ fontSize: 9 }}
            />

            <Tooltip
              formatter={(value) => [
                Number(value).toFixed(3),
                "RMSE",
              ]}
            />

            <Bar
              dataKey="rmse"
              fill="#dc2626"
              radius={[0, 4, 4, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>


    {/* FINAL TEST RMSE */}

    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

      <div className="mb-4">
        <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
          FINAL TEST
        </p>

        <h4 className="mt-1 text-base font-bold text-gray-900">
          RMSE Comparison
        </h4>

        <p className="mt-1 text-xs text-gray-500">
          Final test-period error with greater sensitivity to larger misses.
        </p>
      </div>

      <div className="h-[300px] w-full">

        <ResponsiveContainer width="100%" height="100%">

          <BarChart
            layout="vertical"
            data={(validationResult.final_test || []).map((item) => ({
              model: item.model,
              rmse: Number(item.rmse),
            }))}
            margin={{
              top: 5,
              right: 20,
              left: 20,
              bottom: 5,
            }}
          >

            <CartesianGrid strokeDasharray="3 3" horizontal={false} />

            <XAxis
              type="number"
              tick={{ fontSize: 10 }}
            />

            <YAxis
              type="category"
              dataKey="model"
              width={95}
              tick={{ fontSize: 9 }}
            />

            <Tooltip
              formatter={(value) => [
                Number(value).toFixed(3),
                "RMSE",
              ]}
            />

            <Bar
              dataKey="rmse"
              fill="#dc2626"
              radius={[0, 4, 4, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>

  </div>


  {/* =================================================
      MAPE
  ================================================= */}

  <div className="grid gap-6 xl:grid-cols-2">

    {/* WALK-FORWARD MAPE */}

    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

      <div className="mb-4">
        <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
          WALK-FORWARD
        </p>

        <h4 className="mt-1 text-base font-bold text-gray-900">
          MAPE Comparison
        </h4>

        <p className="mt-1 text-xs text-gray-500">
          Mean Absolute Percentage Error across validation periods.
        </p>
      </div>

      <div className="h-[300px] w-full">

        <ResponsiveContainer width="100%" height="100%">

          <BarChart
            layout="vertical"
            data={(validationResult.walk_forward || []).map((item) => ({
              model: item.model,
              mape: Number(item.mape),
            }))}
            margin={{
              top: 5,
              right: 20,
              left: 20,
              bottom: 5,
            }}
          >

            <CartesianGrid strokeDasharray="3 3" horizontal={false} />

            <XAxis
              type="number"
              tick={{ fontSize: 10 }}
            />

            <YAxis
              type="category"
              dataKey="model"
              width={95}
              tick={{ fontSize: 9 }}
            />

            <Tooltip
              formatter={(value) => [
                `${Number(value).toFixed(3)}%`,
                "MAPE",
              ]}
            />

            <Bar
              dataKey="mape"
              fill="#dc2626"
              radius={[0, 4, 4, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>


    {/* FINAL TEST MAPE */}

    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

      <div className="mb-4">
        <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
          FINAL TEST
        </p>

        <h4 className="mt-1 text-base font-bold text-gray-900">
          MAPE Comparison
        </h4>

        <p className="mt-1 text-xs text-gray-500">
          Percentage forecast error on the final test period.
        </p>
      </div>

      <div className="h-[300px] w-full">

        <ResponsiveContainer width="100%" height="100%">

          <BarChart
            layout="vertical"
            data={(validationResult.final_test || []).map((item) => ({
              model: item.model,
              mape: Number(item.mape),
            }))}
            margin={{
              top: 5,
              right: 20,
              left: 20,
              bottom: 5,
            }}
          >

            <CartesianGrid strokeDasharray="3 3" horizontal={false} />

            <XAxis
              type="number"
              tick={{ fontSize: 10 }}
            />

            <YAxis
              type="category"
              dataKey="model"
              width={95}
              tick={{ fontSize: 9 }}
            />

            <Tooltip
              formatter={(value) => [
                `${Number(value).toFixed(3)}%`,
                "MAPE",
              ]}
            />

            <Bar
              dataKey="mape"
              fill="#dc2626"
              radius={[0, 4, 4, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>

  </div>


  {/* CHART INTERPRETATION */}

  <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

    <div className="flex items-start gap-3">

      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-50 text-red-600">
        <BarChart3 className="h-4 w-4" />
      </div>

      <div>

        <h4 className="text-sm font-bold text-gray-900">
          How to read these charts
        </h4>

        <p className="mt-2 text-xs leading-5 text-gray-500">
          MAE represents the average absolute forecast error. RMSE
          gives additional weight to larger errors. MAPE expresses
          error as a percentage of the observed value.
        </p>

        <p className="mt-2 text-xs leading-5 text-gray-500">
          The walk-forward charts evaluate repeated historical
          forecasting origins, while the final-test charts evaluate
          the separate April 2024 – March 2025 test period.
        </p>

      </div>

    </div>

  </div>

</div>
        {/* METRIC DEFINITIONS */}

        <div className="grid gap-5 md:grid-cols-3">

          {[
            {
              title: "MAE",
              text: validationResult.metric_definitions?.mae,
            },
            {
              title: "RMSE",
              text: validationResult.metric_definitions?.rmse,
            },
            {
              title: "MAPE",
              text: validationResult.metric_definitions?.mape,
            },
          ].map((metric) => (

            <div
              key={metric.title}
              className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"
            >

              <div className="flex items-center gap-2">

                <div className="h-2.5 w-2.5 rounded-full bg-red-600" />

                <h3 className="text-sm font-bold text-gray-900">
                  {metric.title}
                </h3>

              </div>

              <p className="mt-3 text-xs leading-5 text-gray-500">
                {metric.text}
              </p>

            </div>

          ))}

        </div>

        {/* INTERPRETATION */}

        <div className="rounded-2xl border border-red-200 bg-gradient-to-r from-red-50 via-white to-white p-5 shadow-sm">

          <div className="flex items-start gap-3">

            <Info className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />

            <div>

              <p className="text-sm font-bold text-gray-900">
                Validation interpretation
              </p>

              <p className="mt-2 text-xs leading-5 text-gray-600">
                Lower MAE, RMSE, and MAPE indicate lower historical
                forecast error for the evaluated period. These results
                are specific to this dataset and validation design.
              </p>

              <p className="mt-2 text-xs leading-5 text-gray-600">
                AIC and BIC apply to likelihood-based statistical
                models and are not directly comparable with the
                predictive error metrics of Random Forest, XGBoost,
                LSTM, or GRU.
              </p>

            </div>

          </div>

        </div>

      </>
    )}

  </motion.div>
)}
{/* =================================================
    FORECAST
================================================= */}

{activePage === "FORECAST" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
    className="space-y-6"
  >

    {/* =================================================
        HEADER
    ================================================= */}

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

        <div>

          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            BUSINESS FORECAST
          </p>

          <h2 className="mt-2 text-2xl font-bold text-gray-900">
            Generate Future Predictions
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-500">
            Generate future values from the selected forecasting model
            and use the resulting estimates as planning signals.
          </p>

        </div>

        {modelResult?.forecast?.length > 0 && (
          <button
            type="button"
            onClick={handleExportForecastCsv}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-5 py-3 text-sm font-semibold text-gray-700 shadow-sm transition hover:border-red-300 hover:bg-red-50 hover:text-red-700"
          >
            <FileSpreadsheet className="h-4 w-4" />
            Export CSV
          </button>
        )}

      </div>

    </div>


    {/* =================================================
        FORECAST CONFIGURATION
    ================================================= */}

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

      <div className="mb-5">

        <p className="text-xs font-bold tracking-[0.18em] text-red-600">
          FORECAST CONFIGURATION
        </p>

        <h3 className="mt-2 text-xl font-bold text-gray-900">
          Choose Forecast Settings
        </h3>

        <p className="mt-1 text-sm text-gray-500">
          Select the forecasting approach and future horizon.
        </p>

      </div>


      <div className="grid gap-5 md:grid-cols-3">

        {/* MODEL */}

        <div>

          <label className="mb-2 block text-sm font-semibold text-gray-700">
            Forecasting Model
          </label>

          <select
            value={selectedModel}
            onChange={(event) => {
              setSelectedModel(event.target.value);
              setModelResult(null);
              setModelError("");
            }}
            className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 outline-none focus:border-red-500 focus:ring-2 focus:ring-red-100"
          >

            <option value="tesm">
              TESM / Holt-Winters
            </option>

            <option value="sarima">
              SARIMA
            </option>

            <option value="sarimax">
              SARIMAX
            </option>

            <option value="random_forest">
              Random Forest
            </option>

            <option value="xgboost">
              XGBoost
            </option>

            <option value="lstm">
              LSTM
            </option>

            <option value="gru">
              GRU
            </option>

          </select>

        </div>


        {/* HORIZON */}

        <div>

          <label className="mb-2 block text-sm font-semibold text-gray-700">
            Forecast Horizon
          </label>

          <select
            value={forecastHorizon}
            onChange={(event) =>
              setForecastHorizon(Number(event.target.value))
            }
            className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 outline-none focus:border-red-500 focus:ring-2 focus:ring-red-100"
          >

            <option value={3}>
              3 months
            </option>

            <option value={6}>
              6 months
            </option>

            <option value={12}>
              12 months
            </option>

            <option value={18}>
              18 months
            </option>

            <option value={24}>
              24 months
            </option>

          </select>

        </div>


        {/* TARGET */}

        <div>

          <label className="mb-2 block text-sm font-semibold text-gray-700">
            Forecast Target
          </label>

          <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700">
            {targetColumn || "Not selected"}
          </div>

        </div>

      </div>


      {/* DATE */}

      <div className="mt-5 rounded-xl border border-gray-200 bg-gray-50 p-4">

        <div className="grid gap-4 sm:grid-cols-2">

          <div>
            <p className="text-[10px] font-bold tracking-wider text-gray-400">
              DATE COLUMN
            </p>

            <p className="mt-1 text-sm font-semibold text-gray-800">
              {dateColumn || "Not selected"}
            </p>
          </div>

          <div>
            <p className="text-[10px] font-bold tracking-wider text-gray-400">
              DATASET
            </p>

            <p className="mt-1 text-sm font-semibold text-gray-800">
              {datasetLoaded
                ? "Active dataset"
                : "No dataset loaded"}
            </p>
          </div>

        </div>

      </div>


      {/* RUN */}

      <div className="mt-6 flex justify-end">

        <button
          type="button"
          onClick={handleSelectedModelForecast}
          disabled={modelLoading || !datasetLoaded}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >

          {modelLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Generating Forecast...
            </>
          ) : (
            <>
              <Activity className="h-4 w-4" />
              Generate Forecast
            </>
          )}

        </button>

      </div>


      {/* ERROR */}

      {modelError && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4">

          <div className="flex items-start gap-3">

            <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

            <div>

              <p className="text-sm font-semibold text-red-800">
                Forecast error
              </p>

              <p className="mt-1 text-xs leading-5 text-red-700">
                {modelError}
              </p>

            </div>

          </div>

        </div>
      )}

    </div>


    {/* =================================================
        EMPTY STATE
    ================================================= */}

    {!modelResult && !modelLoading && (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center shadow-sm">

        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-600">
          <Activity className="h-7 w-7" />
        </div>

        <h3 className="mt-4 text-lg font-bold text-gray-900">
          Forecast is ready to generate
        </h3>

        <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-gray-500">
          Select a model and forecast horizon above, then generate
          predictions for your selected target.
        </p>

      </div>
    )}


    {/* =================================================
        FORECAST RESULTS
    ================================================= */}

    {modelResult?.forecast?.length > 0 && (
      <>

        {/* SUMMARY */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

            <p className="text-[10px] font-bold tracking-[0.15em] text-gray-400">
              MODEL
            </p>

            <p className="mt-2 text-lg font-bold text-gray-900">
              {modelResult.model?.name ||
                modelResult.model?.type ||
                selectedModel}
            </p>

          </div>


          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

            <p className="text-[10px] font-bold tracking-[0.15em] text-gray-400">
              HORIZON
            </p>

            <p className="mt-2 text-lg font-bold text-gray-900">
              {modelResult.forecast.length} months
            </p>

          </div>


          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">

            <p className="text-[10px] font-bold tracking-[0.15em] text-gray-400">
              LAST OBSERVED
            </p>

            <p className="mt-2 text-lg font-bold text-gray-900">

              {modelResult.historical?.length
                ? Number(
                    modelResult.historical[
                      modelResult.historical.length - 1
                    ].value
                  ).toFixed(2)
                : "N/A"}

            </p>

          </div>


          <div className="rounded-2xl border border-green-200 bg-green-50 p-5 shadow-sm">

            <p className="text-[10px] font-bold tracking-[0.15em] text-green-600">
              STATUS
            </p>

            <p className="mt-2 text-lg font-bold text-green-700">
              Forecast Ready
            </p>

          </div>

        </div>


        {/* =================================================
            MAIN FORECAST CHART
        ================================================= */}

        {modelChartData.length > 0 && (
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

            <div className="mb-5">

              <p className="text-xs font-bold tracking-[0.18em] text-red-600">
                FORECAST VISUALIZATION
              </p>

              <h3 className="mt-2 text-xl font-bold text-gray-900">
                Historical Values vs Future Forecast
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                Historical observations are shown together with the
                projected future values.
              </p>

            </div>


            <div className="h-[420px] w-full">

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <RechartsLineChart
                  data={modelChartData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 10,
                    bottom: 10,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 10 }}
                    tickMargin={8}
                    minTickGap={35}
                  />

                  <YAxis
                    tick={{ fontSize: 10 }}
                    width={55}
                  />

                  <Tooltip
                    formatter={(value, name) => {

                      if (
                        value === null ||
                        value === undefined
                      ) {
                        return ["-", name];
                      }

                      return [
                        Number(value).toFixed(2),
                        name,
                      ];
                    }}

                    labelFormatter={(label) =>
                      `Date: ${label}`
                    }
                  />


                  {/* HISTORICAL */}

                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Historical"
                    stroke="#374151"
                    strokeWidth={2}
                    dot={false}
                    connectNulls={false}
                  />


                  {/* FORECAST */}

                  <Line
                    type="monotone"
                    dataKey="forecast"
                    name="Forecast"
                    stroke="#dc2626"
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    connectNulls={false}
                  />


                  {/* LOWER INTERVAL */}

                  <Line
                    type="monotone"
                    dataKey="lower"
                    name="Lower interval"
                    stroke="#fca5a5"
                    strokeWidth={1.5}
                    strokeDasharray="5 5"
                    dot={false}
                    connectNulls={false}
                  />


                  {/* UPPER INTERVAL */}

                  <Line
                    type="monotone"
                    dataKey="upper"
                    name="Upper interval"
                    stroke="#fca5a5"
                    strokeWidth={1.5}
                    strokeDasharray="5 5"
                    dot={false}
                    connectNulls={false}
                  />

                </RechartsLineChart>

              </ResponsiveContainer>

            </div>


            <div className="mt-4 flex flex-wrap gap-5 text-xs font-medium text-gray-600">

              <div className="flex items-center gap-2">
                <span className="h-2.5 w-7 rounded-full bg-gray-700" />
                Historical
              </div>

              <div className="flex items-center gap-2">
                <span className="h-2.5 w-7 rounded-full bg-red-600" />
                Forecast
              </div>

              <div className="flex items-center gap-2">
                <span className="h-0 w-7 border-t-2 border-dashed border-red-300" />
                Prediction interval
              </div>

            </div>

          </div>
        )}


        {/* =================================================
            FORECAST TABLE
        ================================================= */}

        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">

          <div className="flex flex-col gap-3 border-b border-gray-100 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">

            <div>

              <p className="text-xs font-bold tracking-[0.18em] text-red-600">
                FORECAST VALUES
              </p>

              <h3 className="mt-1 text-lg font-bold text-gray-900">
                Future Planning Values
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                Projected values for each future period.
              </p>

            </div>

            <button
              type="button"
              onClick={handleExportForecastCsv}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-xs font-semibold text-gray-700 transition hover:border-red-300 hover:bg-red-50 hover:text-red-700"
            >
              <FileSpreadsheet className="h-4 w-4" />
              Export CSV
            </button>

          </div>


          <div className="overflow-x-auto">

            <table className="min-w-full text-sm">

              <thead className="bg-gray-50">

                <tr>

                  <th className="px-6 py-3 text-left font-semibold text-gray-600">
                    Date
                  </th>

                  <th className="px-6 py-3 text-right font-semibold text-gray-600">
                    Forecast
                  </th>

                  <th className="px-6 py-3 text-right font-semibold text-gray-600">
                    Lower
                  </th>

                  <th className="px-6 py-3 text-right font-semibold text-gray-600">
                    Upper
                  </th>

                </tr>

              </thead>


              <tbody className="divide-y divide-gray-100">

                {modelResult.forecast.map(
                  (item, index) => (
                    <tr
                      key={`${item.date}-${index}`}
                      className="transition hover:bg-red-50/40"
                    >

                      <td className="px-6 py-3 font-medium text-gray-800">
                        {item.date}
                      </td>

                      <td className="px-6 py-3 text-right font-bold text-red-600">
                        {Number(item.value).toFixed(2)}
                      </td>

                      <td className="px-6 py-3 text-right text-gray-600">
                        {item.lower !== undefined &&
                        item.lower !== null
                          ? Number(item.lower).toFixed(2)
                          : "—"}
                      </td>

                      <td className="px-6 py-3 text-right text-gray-600">
                        {item.upper !== undefined &&
                        item.upper !== null
                          ? Number(item.upper).toFixed(2)
                          : "—"}
                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

          </div>

        </div>


        {/* =================================================
            MODEL DETAILS
        ================================================= */}

        {(modelResult.parameters ||
          modelResult.model ||
          modelResult.aic !== undefined ||
          modelResult.bic !== undefined) && (

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

            <p className="text-xs font-bold tracking-[0.18em] text-red-600">
              MODEL DETAILS
            </p>

            <h3 className="mt-2 text-lg font-bold text-gray-900">
              Forecast Configuration
            </h3>


            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

              {modelResult.model?.type && (
                <div className="rounded-xl bg-gray-50 p-4">

                  <p className="text-[10px] font-bold tracking-wider text-gray-400">
                    MODEL TYPE
                  </p>

                  <p className="mt-2 text-sm font-bold text-gray-900">
                    {modelResult.model.type}
                  </p>

                </div>
              )}


              {modelResult.aic !== undefined &&
                modelResult.aic !== null && (
                  <div className="rounded-xl bg-gray-50 p-4">

                    <p className="text-[10px] font-bold tracking-wider text-gray-400">
                      AIC
                    </p>

                    <p className="mt-2 text-sm font-bold text-gray-900">
                      {Number(modelResult.aic).toFixed(3)}
                    </p>

                  </div>
                )}


              {modelResult.bic !== undefined &&
                modelResult.bic !== null && (
                  <div className="rounded-xl bg-gray-50 p-4">

                    <p className="text-[10px] font-bold tracking-wider text-gray-400">
                      BIC
                    </p>

                    <p className="mt-2 text-sm font-bold text-gray-900">
                      {Number(modelResult.bic).toFixed(3)}
                    </p>

                  </div>
                )}


              {modelResult.parameters &&
                Object.entries(modelResult.parameters)
                  .slice(0, 4)
                  .map(([key, value]) => (

                    <div
                      key={key}
                      className="rounded-xl bg-gray-50 p-4"
                    >

                      <p className="text-[10px] font-bold tracking-wider text-gray-400">
                        {key.replaceAll("_", " ").toUpperCase()}
                      </p>

                      <p className="mt-2 truncate text-sm font-bold text-gray-900">
                        {typeof value === "number"
                          ? Number(value).toFixed(4)
                          : String(value)}
                      </p>

                    </div>

                  ))}

            </div>

          </div>
        )}

      </>

    )}

  </motion.div>
)}


{/* =================================================
    EXPLAINABILITY
================================================= */}

{activePage === "EXPLAIN" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
    className="space-y-6"
  >

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            MODEL EXPLAINABILITY
          </p>
          <h2 className="mt-2 text-2xl font-bold text-gray-900">
            Why This Forecast?
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-500">
            Inspect feature attribution and model metadata when the selected
            forecasting model provides explainability information. Attribution
            describes model behavior and does not establish business causality.
          </p>
        </div>

        <button
          type="button"
          onClick={handleExplainability}
          disabled={explainLoading || !datasetLoaded}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {explainLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              Load Explainability
            </>
          )}
        </button>
      </div>
    </div>

    {explainError && (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />
          <div>
            <p className="text-sm font-semibold text-red-800">
              Explainability service
            </p>
            <p className="mt-1 text-xs leading-5 text-red-700">
              {explainError}
            </p>
            <p className="mt-2 text-[11px] leading-5 text-red-600">
              Explainability is connected to the ForecastIQ attribution service.
              Random Forest and XGBoost can display saved SHAP feature attribution.
            </p>
          </div>
        </div>
      </div>
    )}

    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[
        [
          "MODEL",
          modelResult?.model?.name ||
            modelResult?.model?.type ||
            getModelDisplayName(selectedModel),
          "Selected forecasting method",
        ],
        [
          "TARGET",
          targetColumn || "Not selected",
          "Forecast variable",
        ],
        [
          "HORIZON",
          modelResult?.forecast?.length ?? forecastHorizon,
          "Forecast periods",
        ],
        [
          "INTERPRETATION",
          "Attribution",
          "Not causality",
        ],
      ].map(([label, value, detail], index) => (
        <div
          key={label}
          className={`rounded-2xl border p-5 shadow-sm ${
            index === 3
              ? "border-green-200 bg-green-50"
              : "border-gray-200 bg-white"
          }`}
        >
          <p
            className={`text-[10px] font-bold tracking-[0.15em] ${
              index === 3
                ? "text-green-600"
                : "text-gray-400"
            }`}
          >
            {label}
          </p>
          <p
            className={`mt-2 text-lg font-bold ${
              index === 3
                ? "text-green-700"
                : "text-gray-900"
            }`}
          >
            {value}
          </p>
          <p
            className={`mt-1 text-xs ${
              index === 3
                ? "text-green-700/80"
                : "text-gray-500"
            }`}
          >
            {detail}
          </p>
        </div>
      ))}
    </div>

    {!modelResult && !explainResult && (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center shadow-sm">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-600">
          <Sparkles className="h-7 w-7" />
        </div>
        <h3 className="mt-4 text-lg font-bold text-gray-900">
          Run a forecasting model first
        </h3>
        <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-gray-500">
          Model explainability is most useful after a forecast has been
          generated. Run a model from MODELS or FORECAST and return here.
        </p>
        <button
          type="button"
          onClick={() => navigateTo("MODELS")}
          className="mt-5 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-red-700"
        >
          Go to Models
        </button>
      </div>
    )}

    {modelResult && (
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-5">
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            MODEL CONTEXT
          </p>
          <h3 className="mt-2 text-xl font-bold text-gray-900">
            Forecast configuration
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            These values describe the model used to produce the current forecast.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            [
              "MODEL TYPE",
              modelResult.model?.type ||
                modelResult.model?.name ||
                getModelDisplayName(selectedModel),
            ],
            [
              "OBSERVATIONS",
              modelResult.model?.observations ?? "—",
            ],
            [
              "AIC",
              modelResult.aic !== undefined &&
              modelResult.aic !== null
                ? Number(modelResult.aic).toFixed(3)
                : modelResult.model?.aic !== undefined
                ? Number(modelResult.model.aic).toFixed(3)
                : "N/A",
            ],
            [
              "BIC",
              modelResult.bic !== undefined &&
              modelResult.bic !== null
                ? Number(modelResult.bic).toFixed(3)
                : modelResult.model?.bic !== undefined
                ? Number(modelResult.model.bic).toFixed(3)
                : "N/A",
            ],
          ].map(([label, value]) => (
            <div
              key={label}
              className="rounded-xl bg-gray-50 p-4"
            >
              <p className="text-[9px] font-bold tracking-wider text-gray-400">
                {label}
              </p>
              <p className="mt-2 text-sm font-bold text-gray-900">
                {value}
              </p>
            </div>
          ))}
        </div>
      </div>
    )}

    {(() => {
      const rawFeatures =
        explainResult?.features ||
        explainResult?.feature_importance ||
        explainResult?.shap_importance ||
        explainResult?.attributions ||
        modelResult?.feature_importance ||
        modelResult?.shap_importance ||
        [];

      const featureRows = Array.isArray(rawFeatures)
        ? rawFeatures
        : Object.entries(rawFeatures || {}).map(
            ([feature, value]) => ({
              feature,
              importance: value,
            })
          );

      const explainMethod =
        explainResult?.method ||
        "Model-specific attribution";

      const explainParameters =
        explainResult?.parameters || {};

      const explainParameterEntries =
        Object.entries(explainParameters);

      const normalizedFeatures = featureRows
        .map((item, index) => ({
          feature:
            item.feature ||
            item.name ||
            item.column ||
            `Feature ${index + 1}`,
          importance: Number(
            item.importance ??
              item.mean_abs_shap ??
              item.value ??
              item.score ??
              0
          ),
        }))
        .filter((item) => Number.isFinite(item.importance))
        .sort(
          (a, b) =>
            Math.abs(b.importance) -
            Math.abs(a.importance)
        )
        .slice(0, 20);

      const maxImportance = Math.max(
        ...normalizedFeatures.map((item) =>
          Math.abs(item.importance)
        ),
        1
      );

      return (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-xs font-bold tracking-[0.18em] text-red-600">
              FEATURE ATTRIBUTION
            </p>
            <h3 className="mt-2 text-xl font-bold text-gray-900">
              Model drivers
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Dataset-specific attribution for the selected forecasting model.
            </p>

            <div className="mt-4 rounded-xl border border-gray-100 bg-gray-50 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-white px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-gray-700">
                  Method
                </span>
                <span className="text-xs font-semibold text-gray-800">
                  {explainMethod}
                </span>
              </div>

              {explainParameterEntries.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {explainParameterEntries.map(([key, value]) => (
                    <span
                      key={key}
                      className="rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-[10px] text-gray-600"
                    >
                      <span className="font-bold text-gray-800">
                        {key.replaceAll("_", " ")}:
                      </span>{" "}
                      {Array.isArray(value)
                        ? value.join(", ")
                        : typeof value === "object" && value !== null
                        ? JSON.stringify(value)
                        : String(value)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {normalizedFeatures.length > 0 ? (
            <div className="space-y-3">
              {normalizedFeatures.map((item, index) => {
                const width = Math.min(
                  100,
                  (Math.abs(item.importance) /
                    maxImportance) *
                    100
                );

                return (
                  <div
                    key={`${item.feature}-${index}`}
                    className="rounded-xl border border-gray-100 bg-gray-50 p-4"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div className="min-w-0">
                        <p className="truncate text-xs font-bold text-gray-800">
                          {item.feature}
                        </p>
                        <p className="mt-1 text-[10px] text-gray-400">
                          Absolute attribution magnitude
                        </p>
                      </div>

                      <span className="shrink-0 text-xs font-bold text-gray-900">
                        {item.importance.toFixed(4)}
                      </span>
                    </div>

                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-gray-200">
                      <div
                        className="h-full rounded-full bg-red-600 transition-all"
                        style={{ width: `${width}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
              <Sparkles className="mx-auto h-7 w-7 text-gray-300" />
              <p className="mt-3 text-sm font-semibold text-gray-700">
                No feature attribution returned yet
              </p>
              <p className="mx-auto mt-2 max-w-lg text-xs leading-5 text-gray-500">
                The current forecasting response does not contain feature
                attribution. Random Forest and XGBoost can use the project's
                SHAP/native contribution pipeline once the explainability
                endpoint is connected.
              </p>
            </div>
          )}
        </div>
      );
    })()}

    <div className="grid gap-5 md:grid-cols-2">
      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50 text-red-600">
            <Info className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-bold text-gray-900">
            What attribution means
          </h3>
        </div>
        <p className="mt-3 text-xs leading-5 text-gray-500">
          Attribution measures how input signals contributed to a model
          prediction under the selected explanation method. A large
          attribution means the feature was influential for the model output;
          it does not establish a real-world causal relationship.
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-50 text-gray-700">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-bold text-gray-900">
            Use explanations responsibly
          </h3>
        </div>
        <p className="mt-3 text-xs leading-5 text-gray-500">
          Review data quality, forecast error, anomalies, structural breaks,
          and operational context alongside feature attribution. Explanations
          should support model review rather than replace domain validation.
        </p>
      </div>
    </div>

    <div className="rounded-2xl border border-red-200 bg-gradient-to-r from-red-50 via-white to-white p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <Sparkles className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
        <div>
          <p className="text-sm font-bold text-gray-900">
            Explainability roadmap
          </p>
          <ul className="mt-3 space-y-2 text-xs leading-5 text-gray-600">
            <li>• SHAP global feature importance for tree-based models.</li>
            <li>• Local SHAP contributions for individual forecast periods.</li>
            <li>• Native XGBoost contribution fallback.</li>
            <li>• Feature contribution comparison across models.</li>
            <li>• Explicit separation between attribution and causal interpretation.</li>
          </ul>
        </div>
      </div>
    </div>

  </motion.div>
)}




{/* =================================================
    ADMINISTRATION
================================================= */}

{activePage === "ADMIN" && authUser?.role === "admin" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
    className="space-y-6"
  >
    <div className="rounded-2xl border border-red-200 bg-gradient-to-r from-red-50 via-white to-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">ADMINISTRATIVE CONTROL</p>
          <h2 className="mt-2 text-2xl font-bold text-gray-900">ForecastIQ Administration</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-600">
            A controlled administrative workspace for account oversight, audit review,
            report visibility, and system monitoring. Passwords and password hashes are never displayed.
          </p>
        </div>
        <button
          type="button"
          onClick={loadAdminOverview}
          disabled={adminLoading}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-red-600 px-4 py-3 text-xs font-bold text-white transition hover:bg-red-700 disabled:opacity-60"
        >
          <RefreshCcw className={`h-4 w-4 ${adminLoading ? "animate-spin" : ""}`} />
          Refresh administration
        </button>
      </div>
    </div>

    {adminError && (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
        {adminError}
      </div>
    )}

    {adminLoading && !adminOverview ? (
      <div className="rounded-2xl border border-gray-200 bg-white p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-6 w-6 animate-spin text-red-600" />
        <p className="mt-3 text-sm font-semibold text-gray-600">Loading administrative information...</p>
      </div>
    ) : adminOverview ? (
      <>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ["Users", adminOverview.summary?.total_users ?? 0, Users],
            ["Active", adminOverview.summary?.active_users ?? 0, CheckCircle2],
            ["Datasets", adminOverview.summary?.total_datasets ?? 0, Database],
            ["Reports", adminOverview.summary?.total_reports ?? 0, FileText],
          ].map(([label, value, Icon]) => (
            <div key={label} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-bold tracking-[0.16em] text-gray-400">{label}</p>
                <Icon className="h-4 w-4 text-red-600" />
              </div>
              <p className="mt-3 text-3xl font-bold text-gray-900">{value}</p>
            </div>
          ))}
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <UserCog className="h-5 w-5 text-red-600" />
            <div>
              <p className="text-xs font-bold tracking-[0.18em] text-red-600">ACCOUNT OVERSIGHT</p>
              <h3 className="mt-1 text-lg font-bold text-gray-900">User access management</h3>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-[10px] font-bold text-gray-400">USER</th>
                  <th className="px-4 py-3 text-[10px] font-bold text-gray-400">ROLE</th>
                  <th className="px-4 py-3 text-[10px] font-bold text-gray-400">STATUS</th>
                  <th className="px-4 py-3 text-[10px] font-bold text-gray-400">LAST LOGIN</th>
                  <th className="px-4 py-3 text-right text-[10px] font-bold text-gray-400">CONTROL</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {(adminOverview.users || []).map((user) => (
                  <tr key={user.id}>
                    <td className="px-4 py-3">
                      <p className="text-xs font-bold text-gray-800">{user.name}</p>
                      <p className="mt-1 text-[10px] text-gray-400">{user.email}</p>
                    </td>
                    <td className="px-4 py-3 text-xs font-semibold text-gray-600">{user.role}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold ${user.is_active ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                        {user.is_active ? "ACTIVE" : "INACTIVE"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">{user.last_login_at || "Never"}</td>
                    <td className="px-4 py-3 text-right">
                      {user.role === "user" ? (
                        <button
                          type="button"
                          onClick={() => updateUserStatus(user.id, !user.is_active)}
                          className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-[10px] font-bold text-gray-700 hover:border-red-200 hover:bg-red-50 hover:text-red-700"
                        >
                          {user.is_active ? "Deactivate" : "Activate"}
                        </button>
                      ) : (
                        <span className="text-[10px] font-semibold text-gray-400">Protected admin</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <Activity className="h-5 w-5 text-red-600" />
              <div>
                <p className="text-xs font-bold tracking-[0.18em] text-red-600">AUDIT REVIEW</p>
                <h3 className="mt-1 text-lg font-bold text-gray-900">Recent activity</h3>
              </div>
            </div>
            <div className="space-y-3">
              {(adminOverview.activity || []).slice(0, 10).map((item) => (
                <div key={item.id} className="rounded-xl border border-gray-100 bg-gray-50 p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-bold text-gray-800">{item.action}</p>
                      <p className="mt-1 text-[10px] text-gray-500">{item.user?.email || "System"}</p>
                    </div>
                    <span className="text-[9px] text-gray-400">{item.created_at}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <FileText className="h-5 w-5 text-red-600" />
              <div>
                <p className="text-xs font-bold tracking-[0.18em] text-red-600">REPORT OVERSIGHT</p>
                <h3 className="mt-1 text-lg font-bold text-gray-900">Recent reports</h3>
              </div>
            </div>
            <div className="space-y-3">
              {(adminOverview.reports || []).slice(0, 10).map((item) => (
                <div key={item.report_id} className="rounded-xl border border-gray-100 bg-gray-50 p-3">
                  <p className="text-xs font-bold text-gray-800">{item.dataset_filename || "Dataset report"}</p>
                  <p className="mt-1 text-[10px] text-gray-500">{item.owner?.email || "Unknown owner"}</p>
                  <div className="mt-2 flex items-center justify-between gap-3">
                    <span className="text-[9px] text-gray-400">{item.created_at}</span>
                    <span className="rounded-full bg-white px-2 py-1 text-[9px] font-bold text-gray-500">{item.review_status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
            <div>
              <p className="text-sm font-bold text-gray-900">Administrative authority and safeguards</p>
              <p className="mt-2 text-xs leading-5 text-gray-600">
                Administrators can oversee user access, review audit activity, inspect report ownership,
                and monitor database status. Administrators cannot view plaintext passwords or password hashes,
                and normal users cannot access this administrative workspace.
              </p>
            </div>
          </div>
        </div>
      </>
    ) : null}
  </motion.div>
)}


{/* =================================================
    REPORT
================================================= */}

{activePage === "REPORT" && (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
    className="space-y-6"
  >

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            BUSINESS REPORTING
          </p>
          <h2 className="mt-2 text-2xl font-bold text-gray-900">
            Management Review Forecasting Report
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-500">
            Consolidate dataset quality, historical patterns, anomalies,
            model validation, forecast values, and explainability into a
            factual management-review summary.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={handlePrintReport}
            className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm font-semibold text-gray-700 transition hover:border-red-300 hover:bg-red-50 hover:text-red-700"
          >
            <FileText className="h-4 w-4" />
            Print / Save PDF
          </button>

          <button
            type="button"
            onClick={handleExportReportJson}
            disabled={reportLoading}
            className="inline-flex items-center gap-2 rounded-xl bg-red-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-50"
          >
            {reportLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="h-4 w-4" />
            )}
            Generate PDF + JSON
          </button>
        </div>
      </div>
    </div>

    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {[
        {
          label: "DATA",
          ready: datasetLoaded,
          detail: datasetLoaded ? "Loaded" : "Required",
        },
        {
          label: "PROFILE",
          ready: Boolean(datasetProfile),
          detail: datasetProfile ? "Available" : "Pending",
        },
        {
          label: "EXPLORE",
          ready: Boolean(exploreResult),
          detail: exploreResult ? "Analyzed" : "Pending",
        },
        {
          label: "VALIDATE",
          ready: Boolean(validationResult),
          detail: validationResult ? "Completed" : "Pending",
        },
        {
          label: "FORECAST",
          ready: Boolean(modelResult?.forecast?.length),
          detail: modelResult?.forecast?.length
            ? "Generated"
            : "Pending",
        },
      ].map((item) => (
        <div
          key={item.label}
          className={`rounded-2xl border p-5 shadow-sm ${
            item.ready
              ? "border-green-200 bg-green-50"
              : "border-gray-200 bg-white"
          }`}
        >
          <div className="flex items-center justify-between">
            <p
              className={`text-[10px] font-bold tracking-[0.15em] ${
                item.ready
                  ? "text-green-600"
                  : "text-gray-400"
              }`}
            >
              {item.label}
            </p>

            {item.ready ? (
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            ) : (
              <Info className="h-4 w-4 text-gray-400" />
            )}
          </div>

          <p
            className={`mt-3 text-sm font-bold ${
              item.ready
                ? "text-green-700"
                : "text-gray-800"
            }`}
          >
            {item.detail}
          </p>
        </div>
      ))}
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-50 text-red-600">
          <Database className="h-5 w-5" />
        </div>
        <div>
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            DATASET SUMMARY
          </p>
          <h3 className="mt-2 text-xl font-bold text-gray-900">
            {selectedFile?.name || "No dataset loaded"}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Target: {targetColumn || "—"} · Date: {dateColumn || "—"}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          [
            "OBSERVATIONS",
            datasetProfile?.rows ??
              quality.rows ??
              "—",
          ],
          [
            "VARIABLES",
            datasetProfile?.columns ??
              quality.columns ??
              "—",
          ],
          [
            "MISSING",
            datasetProfile?.missing_cells ??
              quality.missing ??
              "—",
          ],
          [
            "DUPLICATES",
            datasetProfile?.duplicate_rows ??
              quality.duplicates ??
              "—",
          ],
        ].map(([label, value]) => (
          <div
            key={label}
            className="rounded-xl bg-gray-50 p-4"
          >
            <p className="text-[9px] font-bold tracking-wider text-gray-400">
              {label}
            </p>
            <p className="mt-2 text-lg font-bold text-gray-900">
              {value}
            </p>
          </div>
        ))}
      </div>
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <p className="text-xs font-bold tracking-[0.18em] text-red-600">
          HISTORICAL ANALYSIS
        </p>
        <h3 className="mt-2 text-xl font-bold text-gray-900">
          Trend and statistical findings
        </h3>
      </div>

      {exploreResult ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            [
              "OBSERVATIONS",
              exploreResult.rows_analyzed ?? "—",
            ],
            [
              "TREND",
              exploreResult.trend ?? "—",
            ],
            [
              "ADF P-VALUE",
              exploreResult.adf?.p_value !== undefined
                ? Number(
                    exploreResult.adf.p_value
                  ).toFixed(6)
                : "—",
            ],
            [
              "STATIONARY",
              exploreResult.adf?.stationary === true
                ? "YES"
                : exploreResult.adf?.stationary === false
                ? "NO"
                : "—",
            ],
          ].map(([label, value]) => (
            <div
              key={label}
              className="rounded-xl border border-gray-200 bg-gray-50 p-4"
            >
              <p className="text-[9px] font-bold tracking-wider text-gray-400">
                {label}
              </p>
              <p className="mt-2 text-sm font-bold text-gray-900">
                {value}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-center">
          <p className="text-sm font-semibold text-gray-700">
            Exploration results have not been loaded.
          </p>
          <button
            type="button"
            onClick={() => navigateTo("EXPLORE")}
            className="mt-4 rounded-lg bg-red-600 px-5 py-2.5 text-xs font-bold text-white"
          >
            Go to Explore
          </button>
        </div>
      )}
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <p className="text-xs font-bold tracking-[0.18em] text-red-600">
          RISK REVIEW
        </p>
        <h3 className="mt-2 text-xl font-bold text-gray-900">
          Anomaly summary
        </h3>
      </div>

      {anomalyResult ? (
        <div className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              [
                "TOTAL",
                anomalyResult?.summary?.total_anomalies ?? 0,
              ],
              [
                "HIGH",
                anomalyResult?.summary?.high ?? 0,
              ],
              [
                "MEDIUM",
                anomalyResult?.summary?.medium ?? 0,
              ],
              [
                "LOW",
                anomalyResult?.summary?.low ?? 0,
              ],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-xl bg-gray-50 p-4"
              >
                <p className="text-[9px] font-bold tracking-wider text-gray-400">
                  {label}
                </p>
                <p className="mt-2 text-xl font-bold text-gray-900">
                  {value}
                </p>
              </div>
            ))}
          </div>

          <p className="text-xs leading-5 text-gray-500">
            {anomalyResult?.timeline?.length ?? 0} anomaly observations are
            available for detailed review.
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-center">
          <p className="text-sm font-semibold text-gray-700">
            Anomaly analysis has not been loaded.
          </p>
          <button
            type="button"
            onClick={() => navigateTo("ANOMALIES")}
            className="mt-4 rounded-lg bg-red-600 px-5 py-2.5 text-xs font-bold text-white"
          >
            Go to Anomalies
          </button>
        </div>
      )}
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <p className="text-xs font-bold tracking-[0.18em] text-red-600">
          MODEL VALIDATION
        </p>
        <h3 className="mt-2 text-xl font-bold text-gray-900">
          Historical forecast reliability
        </h3>
      </div>

      {validationResult ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                  MODEL
                </th>
                <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                  MAE
                </th>
                <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                  RMSE
                </th>
                <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                  MAPE
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100">
              {(validationResult.final_test || []).map(
                (item) => (
                  <tr
                    key={item.model}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-4 py-3 text-xs font-semibold text-gray-800">
                      {item.model}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">
                      {Number(item.mae).toFixed(3)}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">
                      {Number(item.rmse).toFixed(3)}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">
                      {Number(item.mape).toFixed(3)}%
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-center">
          <p className="text-sm font-semibold text-gray-700">
            Validation results have not been loaded.
          </p>
          <button
            type="button"
            onClick={() => navigateTo("VALIDATE")}
            className="mt-4 rounded-lg bg-red-600 px-5 py-2.5 text-xs font-bold text-white"
          >
            Go to Validate
          </button>
        </div>
      )}
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.18em] text-red-600">
            FORECAST OUTPUT
          </p>
          <h3 className="mt-2 text-xl font-bold text-gray-900">
            Future planning values
          </h3>
        </div>

        {modelResult?.forecast?.length > 0 && (
          <span className="rounded-full border border-green-200 bg-green-50 px-3 py-1.5 text-[10px] font-bold text-green-700">
            FORECAST AVAILABLE
          </span>
        )}
      </div>

      {modelResult?.forecast?.length > 0 ? (
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[700px] text-left">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-[10px] font-bold tracking-wider text-gray-400">
                  PERIOD
                </th>
                <th className="px-4 py-3 text-right text-[10px] font-bold tracking-wider text-gray-400">
                  FORECAST
                </th>
                <th className="px-4 py-3 text-right text-[10px] font-bold tracking-wider text-gray-400">
                  LOWER
                </th>
                <th className="px-4 py-3 text-right text-[10px] font-bold tracking-wider text-gray-400">
                  UPPER
                </th>
                <th className="px-4 py-3 text-right text-[10px] font-bold tracking-wider text-gray-400">
                  WIDTH
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100">
              {modelResult.forecast.map(
                (item, index) => (
                  <tr
                    key={`${item.date}-${index}`}
                    className="hover:bg-red-50/30"
                  >
                    <td className="px-4 py-3 text-xs font-semibold text-gray-800">
                      {item.date}
                    </td>
                    <td className="px-4 py-3 text-right text-xs font-bold text-red-600">
                      {Number(item.value).toFixed(2)}
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-gray-600">
                      {item.lower !== undefined &&
                      item.lower !== null
                        ? Number(item.lower).toFixed(2)
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-gray-600">
                      {item.upper !== undefined &&
                      item.upper !== null
                        ? Number(item.upper).toFixed(2)
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-gray-600">
                      {item.lower !== undefined &&
                      item.lower !== null &&
                      item.upper !== undefined &&
                      item.upper !== null
                        ? (
                            Number(item.upper) -
                            Number(item.lower)
                          ).toFixed(2)
                        : "—"}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="mt-5 rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 text-center">
          <p className="text-sm font-semibold text-gray-700">
            No forecast has been generated yet.
          </p>
          <button
            type="button"
            onClick={() => navigateTo("FORECAST")}
            className="mt-4 rounded-lg bg-red-600 px-5 py-2.5 text-xs font-bold text-white"
          >
            Generate Forecast
          </button>
        </div>
      )}
    </div>

    <div className="rounded-2xl border border-red-200 bg-gradient-to-r from-red-50 via-white to-white p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <Info className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
        <div>
          <p className="text-sm font-bold text-gray-900">
            Reporting guidance
          </p>
          <p className="mt-2 text-xs leading-5 text-gray-600">
            The report is an analytical evidence summary, not an automatic business
            decision or approval. Review forecast intervals, validation error, anomaly
            periods, structural changes, known events, and operational
            constraints before committing resources.
          </p>
          <p className="mt-2 text-xs leading-5 text-gray-600">
            Print / Save PDF uses the browser print workflow. JSON export
            is intended for downstream integration and future server-side
            report generation.
          </p>
        </div>
      </div>
    </div>

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <p className="text-xs font-bold tracking-[0.18em] text-red-600">
          REPORTING ROADMAP
        </p>
        <h3 className="mt-2 text-xl font-bold text-gray-900">
          Reporting and governance roadmap
        </h3>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[
          [
            "PDF generation",
            "Server-side PDF reports with branded charts, tables, methodology, and model results.",
          ],
          [
            "Scheduled reports",
            "Automated daily, weekly, or monthly reporting for operational teams.",
          ],
          [
            "Report versioning",
            "Store forecast runs, model configurations, metrics, and assumptions for auditability.",
          ],
          [
            "Scenario analysis",
            "Compare baseline, optimistic, conservative, and event-adjusted planning scenarios.",
          ],
          [
            "Database persistence",
            "Store datasets, model runs, validation results, forecasts, and reports in PostgreSQL.",
          ],
          [
            "Cloud deployment",
            "Separate frontend, Flask/ML services, object storage, and managed database infrastructure.",
          ],
        ].map(([title, description]) => (
          <div
            key={title}
            className="rounded-xl border border-gray-200 bg-gray-50 p-4"
          >
            <p className="text-sm font-bold text-gray-900">
              {title}
            </p>
            <p className="mt-2 text-xs leading-5 text-gray-500">
              {description}
            </p>
          </div>
        ))}
      </div>
    </div>

    <div className="flex justify-end">
      <button
        type="button"
        onClick={handleResetAnalysis}
        className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-xs font-semibold text-gray-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700"
      >
        <RefreshCcw className="h-4 w-4" />
        Clear Analysis Results
      </button>
    </div>

  </motion.div>
)}

{/* =================================================
    DATA HOME
================================================= */}
            {activePage === "DATA" && (
              <>
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.45 }}
                  className="relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:p-8"
                >

                  <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-red-100 blur-3xl" />

                  <div className="relative max-w-3xl">

                    <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-red-200 bg-red-50 px-3 py-1.5 text-[10px] font-bold tracking-wider text-red-700">

                      <Sparkles className="h-3.5 w-3.5" />

                      FORECASTIQ BUSINESS INTELLIGENCE

                    </div>

                    <h1 className="text-3xl font-bold leading-tight tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">

                      Turn business data into

                      <span className="block text-red-600">
                        actionable forecasts.
                      </span>

                    </h1>

                    <p className="mt-5 max-w-2xl text-sm leading-6 text-gray-500 sm:text-base">

                      Upload historical business data, check its quality,
                      understand trends and anomalies, compare forecasting
                      models, and generate explainable planning forecasts.

                    </p>

                    <div className="mt-7 flex flex-wrap gap-3">

                      <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-red-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-red-600/20 transition hover:bg-red-700">

                        {isLoading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Upload className="h-4 w-4" />
                        )}

                        {isLoading ? "Processing..." : "Upload Dataset"}

                        <input
                          type="file"
                          accept=".csv,.xlsx,.xls"
                          className="hidden"
                          onChange={handleFileChange}
                          disabled={isLoading}
                        />

                      </label>

                      <button
                        type="button"
                        onClick={loadDemoDataset}
                        disabled={isLoading}
                        className="rounded-lg border border-gray-200 bg-white px-5 py-3 text-sm font-semibold text-gray-700 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Explore Demo Dataset
                      </button>

                    </div>

                    {uploadError && (
                      <div className="mt-4 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-xs font-medium text-red-700">

                        <AlertTriangle className="h-4 w-4 shrink-0" />

                        {uploadError}

                      </div>
                    )}

                  </div>
                </motion.div>

                {/* =================================================
                    STAT CARDS
                ================================================= */}

                <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

                  {stats.map((stat, index) => {
                    const Icon = stat.icon;

                    return (
                      <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{
                          duration: 0.4,
                          delay: index * 0.05,
                        }}
                        className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-red-200 hover:shadow-md"
                      >

                        <div className="flex items-center justify-between">

                          <span className="text-[10px] font-bold tracking-[0.18em] text-gray-400">
                            {stat.label}
                          </span>

                          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-50">

                            <Icon className="h-4 w-4 text-red-600" />

                          </div>

                        </div>

                        <div className="mt-4 text-2xl font-bold text-gray-900">
                          {stat.value}
                        </div>

                        <p className="mt-1 text-xs text-gray-500">
                          {stat.detail}
                        </p>

                      </motion.div>
                    );
                  })}

                </div>

                {/* =================================================
                    WORKFLOW
                ================================================= */}

                <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">

                  <div className="mb-5">

                    <p className="text-xs font-bold tracking-wider text-gray-800">
                      ANALYTICS WORKFLOW
                    </p>

                    <p className="mt-1 text-xs text-gray-500">
                      Complete the forecasting pipeline step by step.
                    </p>

                  </div>

                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">

                    {workflow.slice(0, 5).map(
                      ([number, title, description]) => (
                        <button
                          key={number}
                          onClick={() => navigateTo(title)}
                          className="group rounded-lg border border-gray-200 bg-gray-50 p-4 text-left transition hover:border-red-200 hover:bg-red-50/40"
                        >

                          <div className="flex items-center justify-between">

                            <span className="text-[10px] font-bold text-red-600">
                              {number}
                            </span>

                            <span className="h-1.5 w-1.5 rounded-full bg-gray-300 transition group-hover:bg-red-600" />

                          </div>

                          <div className="mt-4 text-xs font-bold tracking-wide text-gray-800">
                            {title}
                          </div>

                          <div className="mt-1 text-[11px] text-gray-500">
                            {description}
                          </div>

                        </button>
                      ),
                    )}

                  </div>
                </div>

                {/* =================================================
                    DATASET STATUS
                ================================================= */}

                <div className="mt-6 grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">

                  <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">

                    <div className="flex items-center justify-between">

                      <div>

                        <p className="text-xs font-bold tracking-wider text-gray-800">
                          CURRENT DATASET
                        </p>

                        <p className="mt-1 text-xs text-gray-500">
                          {datasetLoaded
                            ? selectedFile?.name
                            : "No dataset selected"}
                        </p>

                      </div>

                      {datasetLoaded && (
                        <span className="rounded-full border border-green-200 bg-green-50 px-2.5 py-1 text-[10px] font-bold text-green-700">
                          READY
                        </span>
                      )}

                    </div>

                    <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">

                      {[
                        ["ROWS", datasetLoaded ? quality.rows : "—"],
                        [
                          "COLUMNS",
                          datasetLoaded ? quality.columns : "—",
                        ],
                        ["FREQUENCY", datasetLoaded ? "MONTHLY" : "—"],
                        [
                          "COVERAGE",
                          datasetLoaded ? quality.dateRange : "—",
                        ],
                      ].map(([label, value]) => (
                        <div
                          key={label}
                          className="rounded-lg border border-gray-200 bg-gray-50 p-3"
                        >

                          <p className="text-[9px] font-semibold tracking-wider text-gray-400">
                            {label}
                          </p>

                          <p className="mt-1 text-xs font-bold text-gray-800">
                            {value}
                          </p>

                        </div>
                      ))}

                    </div>

                  </div>

                  <div className="rounded-xl border border-red-200 bg-gradient-to-br from-red-50 to-white p-5 shadow-sm">

                    <div className="flex items-center gap-2">

                      <Activity className="h-4 w-4 text-red-600" />

                      <p className="text-xs font-bold tracking-wider text-gray-800">
                        NEXT ACTION
                      </p>

                    </div>

                    <p className="mt-4 text-sm font-bold text-gray-900">
                      {datasetLoaded
                        ? "Review dataset profile"
                        : "Upload a dataset"}
                    </p>

                    <p className="mt-2 text-xs leading-5 text-gray-500">

                      {datasetLoaded
                        ? "Review columns, data quality, date coverage, and target configuration."
                        : "Start by uploading a CSV or Excel time-series dataset."}

                    </p>

                    <button
                      onClick={() =>
                        datasetLoaded
                          ? setShowDataWorkspace(true)
                          : document
                              .getElementById("hidden-upload-trigger")
                              ?.click()
                      }
                      className="mt-5 w-full rounded-lg bg-red-600 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-red-700"
                    >
                      {datasetLoaded ? "Review Dataset →" : "Upload Dataset →"}
                    </button>

                    <input
                      id="hidden-upload-trigger"
                      type="file"
                      accept=".csv,.xlsx,.xls"
                      className="hidden"
                      onChange={handleFileChange}
                    />

                  </div>

                </div>
              </>
            )}

            {/* =================================================
                BUSINESS DECISION PANEL
                A useful business-facing checkpoint shown on every page.
            ================================================= */}
            {(() => {
              const businessPanel = {
                DATA: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: datasetLoaded ? "Your data is ready for analysis" : "Start with the data behind your business decision",
                  text: datasetLoaded
                    ? "You can now assess data quality, understand demand or production patterns, and prepare a forecast for planning."
                    : "Upload historical business data such as sales, demand, production, inventory, orders, traffic, or other time-based measures.",
                  status: datasetLoaded ? "READY FOR ANALYSIS" : "ACTION REQUIRED",
                  action: datasetLoaded ? "Review Data Quality" : "Upload Business Data",
                  next: datasetLoaded ? "PROFILE" : "DATA",
                },
                PROFILE: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Know whether the data can support a forecast",
                  text: datasetProfile
                    ? "Use the quality findings to identify missing values, duplicate records, weak coverage, or column issues before business decisions depend on the forecast."
                    : "A reliable forecast starts with reliable historical data. Load a dataset to see its coverage, quality, and structure.",
                  status: datasetProfile ? "QUALITY REVIEW" : "DATA REQUIRED",
                  action: datasetProfile ? "Prepare Data" : "Go to Dataset",
                  next: datasetProfile ? "CLEAN" : "DATA",
                },
                CLEAN: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Turn raw records into forecast-ready data",
                  text: cleanResult
                    ? "Review the before-and-after quality changes, then continue to trend analysis so the forecasting models work from a controlled dataset."
                    : "Cleaning choices can change the forecast. Keep the original upload untouched and document any missing-value, duplicate, outlier, or transformation treatment.",
                  status: cleanResult ? "PREPARED" : "REVIEW REQUIRED",
                  action: cleanResult ? "Explore Business Trends" : "Prepare Dataset",
                  next: cleanResult ? "EXPLORE" : "CLEAN",
                },
                EXPLORE: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: exploreResult?.trend
                    ? `Historical trend: ${exploreResult.trend}`
                    : "Understand the pattern before planning ahead",
                  text: exploreResult
                    ? `The historical series contains ${exploreResult.rows_analyzed} observations. Use trend, seasonality, and stationarity findings to decide how much confidence to place in future planning.`
                    : "Trend and seasonality help explain recurring business cycles, while stationarity tests help determine which forecasting methods are appropriate.",
                  status: exploreResult ? "PATTERN IDENTIFIED" : "ANALYSIS REQUIRED",
                  action: exploreResult ? "Review Anomalies" : "Run Analysis",
                  next: exploreResult ? "ANOMALIES" : "EXPLORE",
                },
                ANOMALIES: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Separate normal variation from unusual business events",
                  text: "Unexpected spikes, drops, or structural changes can distort forecasts. Review unusual periods before treating them as normal future demand or production behavior.",
                  status: "RISK REVIEW",
                  action: "Configure Forecasting Models",
                  next: "MODELS",
                },
                MODELS: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Compare forecasting approaches for your data",
                  text: "Statistical and machine-learning models capture different patterns. The platform should compare them on historical holdout periods rather than assuming one method works best for every business.",
                  status: "MODEL LAB",
                  action: "Validate Models",
                  next: "VALIDATE",
                },
                VALIDATE: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Measure forecast reliability before using it",
                  text: "Use time-aware backtesting and MAE, RMSE, and MAPE to understand historical forecast error. Lower error indicates closer historical predictions, but business context still matters.",
                  status: "ACCURACY REVIEW",
                  action: "View Business Forecast",
                  next: "FORECAST",
                },
                FORECAST: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Turn predictions into planning signals",
                  text: "Use future estimates to support capacity, inventory, staffing, procurement, sales, or production planning. Forecasts should be reviewed alongside business constraints and known upcoming events.",
                  status: "PLANNING VIEW",
                  action: "Understand Forecast Drivers",
                  next: "EXPLAIN",
                },
                EXPLAIN: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Understand what is driving the forecast",
                  text: "Feature attribution can show which historical signals contributed to a machine-learning prediction. Treat these as model explanations, not proof that a feature caused the business outcome.",
                  status: "DRIVER ANALYSIS",
                  action: "Create Business Report",
                  next: "REPORT",
                },
                REPORT: {
                  eyebrow: "BUSINESS CHECKPOINT",
                  title: "Convert analysis into a decision-ready summary",
                  text: "Bring data quality, historical patterns, anomalies, model validation, forecasts, and model explanations together so teams can review the same evidence before planning decisions are made.",
                  status: "DECISION SUMMARY",
                  action: "Return to Dataset",
                  next: "DATA",
                },
              }[activePage] || {
                eyebrow: "BUSINESS CHECKPOINT",
                title: "Move from data to a measurable business decision",
                text: "Review the current analysis, validate the forecast, and document the assumptions before using predictions for operational planning.",
                status: "WORKFLOW",
                action: "Continue",
                next: "DATA",
              };

              return (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35 }}
                  className="mt-8 rounded-2xl border border-red-200 bg-gradient-to-r from-red-50 via-white to-white p-5 shadow-sm lg:p-6"
                >
                  <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                    <div className="max-w-3xl">
                      <div className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-600 text-white">
                          <Activity className="h-4 w-4" />
                        </div>
                        <p className="text-[10px] font-bold tracking-[0.18em] text-red-600">
                          {businessPanel.eyebrow}
                        </p>
                        <span className="rounded-full border border-red-200 bg-white px-2 py-1 text-[9px] font-bold text-red-700">
                          {businessPanel.status}
                        </span>
                      </div>

                      <h3 className="mt-3 text-base font-bold text-gray-900 lg:text-lg">
                        {businessPanel.title}
                      </h3>

                      <p className="mt-2 text-xs leading-5 text-gray-600 lg:text-sm">
                        {businessPanel.text}
                      </p>
                    </div>

                    <button
                      onClick={() => navigateTo(businessPanel.next)}
                      className="shrink-0 rounded-lg bg-red-600 px-5 py-3 text-xs font-bold text-white shadow-sm transition hover:bg-red-700"
                    >
                      {businessPanel.action} →
                    </button>
                  </div>
                </motion.div>
              );
            })()}

            {/* =================================================
                WORKSPACE PAGE CONTENT
                Page-specific modules are rendered above.
                Generic workspace placeholder removed.
            ================================================= */}

          </section>
        </main>
      </div>

      {/* ========================================================
          DATA WORKSPACE MODAL
      ======================================================== */}

      <AnimatePresence>
        {showDataWorkspace && datasetLoaded && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[80] flex items-center justify-center bg-gray-900/40 p-4 backdrop-blur-sm"
          >

            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.98 }}
              className="max-h-[92vh] w-full max-w-6xl overflow-y-auto rounded-2xl border border-gray-200 bg-white shadow-2xl"
            >

              {/* Modal header */}
              <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-5 py-4">

                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50">

                    <Database className="h-4 w-4 text-red-600" />

                  </div>

                  <div>

                    <h2 className="text-sm font-bold text-gray-900">
                      Dataset Configuration
                    </h2>

                    <p className="text-xs text-gray-500">
                      Validate and configure your time-series data
                    </p>

                  </div>

                </div>

                <button
                  onClick={() => setShowDataWorkspace(false)}
                  className="rounded-lg p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-700"
                >
                  <X className="h-5 w-5" />
                </button>

              </div>

              <div className="p-5 lg:p-6">

                {/* File information */}
                <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">

                  <div className="flex flex-wrap items-center justify-between gap-4">

                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white">

                        <FileSpreadsheet className="h-5 w-5 text-red-600" />

                      </div>

                      <div>

                        <p className="text-xs font-bold text-gray-800">
                          {selectedFile?.name}
                        </p>

                        <p className="mt-1 text-[11px] text-gray-500">
                          {formatBytes(selectedFile?.size)} ·{" "}
                          {getFileExtension(selectedFile?.name || "").toUpperCase()}
                        </p>

                      </div>

                    </div>

                    <button
                      onClick={resetDataset}
                      className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-semibold text-gray-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      Clear
                    </button>

                  </div>

                </div>

                {/* Quality */}
                <div className="mt-5">

                  <div className="mb-3 flex items-center justify-between">

                    <div>

                      <p className="text-xs font-bold tracking-wider text-gray-800">
                        DATA QUALITY
                      </p>

                      <p className="mt-1 text-xs text-gray-500">
                        Initial dataset validation
                      </p>

                    </div>

                    <span className="rounded-full border border-green-200 bg-green-50 px-2.5 py-1 text-[10px] font-bold text-green-700">
                      VALIDATION PASSED
                    </span>

                  </div>

                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

                    {qualityItems.map((item) => (

                      <div
                        key={item.label}
                        className="rounded-xl border border-gray-200 bg-white p-4"
                      >

                        <div className="flex items-center justify-between">

                          <span className="text-[10px] font-bold tracking-wider text-gray-400">
                            {item.label}
                          </span>

                          {item.status === "good" ? (
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-yellow-600" />
                          )}

                        </div>

                        <p className="mt-3 text-xl font-bold text-gray-900">
                          {item.value}
                        </p>

                      </div>

                    ))}

                  </div>

                </div>

                {/* Column mapping */}
                <div className="mt-6 rounded-xl border border-gray-200 bg-white">

                  <div className="border-b border-gray-200 p-4">

                    <p className="text-xs font-bold tracking-wider text-gray-800">
                      COLUMN MAPPING
                    </p>

                    <p className="mt-1 text-xs text-gray-500">
                      Select the date/time column and forecasting target.
                    </p>

                  </div>

                  <div className="grid gap-4 p-4 md:grid-cols-2">

                    <div>

                      <label className="mb-2 block text-xs font-semibold text-gray-700">
                        Date / Time Column
                      </label>

                      <select
                        value={dateColumn}
                        onChange={(event) =>
                          setDateColumn(event.target.value)
                        }
                        className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-xs text-gray-700 outline-none transition focus:border-red-400 focus:ring-2 focus:ring-red-100"
                      >

                        {datasetColumns.map((column) => (
                          <option key={column} value={column}>
                            {column}
                          </option>
                        ))}

                      </select>

                    </div>

                    <div>

                      <label className="mb-2 block text-xs font-semibold text-gray-700">
                        Target Column
                      </label>

                      <select
                        value={targetColumn}
                        onChange={(event) =>
                          setTargetColumn(event.target.value)
                        }
                        className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-xs text-gray-700 outline-none transition focus:border-red-400 focus:ring-2 focus:ring-red-100"
                      >

                        {datasetColumns.map((column) => (
                          <option key={column} value={column}>
                            {column}
                          </option>
                        ))}

                      </select>

                    </div>

                  </div>

                </div>

                {/* Preview */}
                <div className="mt-6 rounded-xl border border-gray-200 bg-white">

                  <div className="flex items-center justify-between border-b border-gray-200 p-4">

                    <div>

                      <p className="text-xs font-bold tracking-wider text-gray-800">
                        DATASET PREVIEW
                      </p>

                      <p className="mt-1 text-xs text-gray-500">
                        First observations from the loaded dataset
                      </p>

                    </div>

                    <Table2 className="h-4 w-4 text-gray-400" />

                  </div>

                  <div className="overflow-x-auto">

                    <table className="w-full min-w-[600px] text-left">

                      <thead className="bg-gray-50">

                        <tr>

                          {datasetColumns.map((column) => (
                            <th
                              key={column}
                              className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-400"
                            >
                              {column}
                            </th>
                          ))}

                        </tr>

                      </thead>

                      <tbody>

                        {rows.map((row, index) => (
                          <tr
                            key={index}
                            className="border-t border-gray-100"
                          >

                            {datasetColumns.map((column) => (
                              <td
                                key={column}
                                className="px-4 py-3 text-xs text-gray-600"
                              >
                                {row[column] ?? "—"}
                              </td>
                            ))}

                          </tr>
                        ))}

                      </tbody>

                    </table>

                  </div>

                </div>

                {/* Configuration summary */}
                <div className="mt-6 rounded-xl border border-red-100 bg-red-50/50 p-4">

                  <div className="flex items-start gap-3">

                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-600" />

                    <div>

                      <p className="text-xs font-bold text-gray-800">
                        Configuration ready
                      </p>

                      <p className="mt-1 text-xs leading-5 text-gray-500">
                        Date column:{" "}
                        <span className="font-semibold text-gray-700">
                          {dateColumn}
                        </span>
                        {" · "}
                        Target column:{" "}
                        <span className="font-semibold text-gray-700">
                          {targetColumn}
                        </span>
                      </p>

                    </div>

                  </div>

                </div>

                {/* Actions */}
                <div className="mt-6 flex flex-col-reverse justify-between gap-3 sm:flex-row">

                  <button
                    onClick={() => setShowDataWorkspace(false)}
                    className="rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-xs font-semibold text-gray-600 transition hover:bg-gray-50"
                  >
                    Close
                  </button>

                  <button
                    onClick={() => {
                      setShowDataWorkspace(false);
                      setActivePage("PROFILE");
                      showToast("Dataset configuration saved.");
                    }}
                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-5 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-red-700"
                  >
                    Continue to Profile
                    <ChevronRight className="h-4 w-4" />
                  </button>

                </div>

              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
