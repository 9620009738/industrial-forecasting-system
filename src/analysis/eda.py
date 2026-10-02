from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DATA_FILE = Path(
    "data/processed/iip_food_products_baseline_2012_2025.csv"
)

GRAPH_DIR = Path("outputs/graphs")


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    return df


def basic_analysis(df):
    print("=" * 60)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    print("\nDataset shape:")
    print(df.shape)

    print("\nData types:")
    print(df.dtypes)

    print("\nDate range:")
    print(
        df["date"].min().date(),
        "to",
        df["date"].max().date()
    )

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDescriptive statistics:")
    print(
        df["index"].describe().to_string()
    )


def create_time_series_plot(df):
    GRAPH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(14, 6))

    plt.plot(
        df["date"],
        df["index"]
    )

    plt.title(
        "India Food Products IIP "
        "(April 2012 – March 2025)"
    )

    plt.xlabel("Date")
    plt.ylabel("IIP Index (2011–12 = 100)")

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = (
        GRAPH_DIR /
        "food_products_iip_time_series.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nTime-series graph saved to:\n"
        f"{output_file}"
    )
def analyze_monthly_seasonality(df):
    print("\n" + "=" * 60)
    print("MONTHLY SEASONALITY ANALYSIS")
    print("=" * 60)

    monthly_average = (
        df.groupby("month", sort=False)["index"]
        .agg(["mean", "std", "min", "max"])
    )

    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    monthly_average = monthly_average.reindex(month_order)

    print("\nAverage IIP by calendar month:")
    print(monthly_average.to_string())

    highest_month = monthly_average["mean"].idxmax()
    lowest_month = monthly_average["mean"].idxmin()

    print(
        f"\nHighest average month: "
        f"{highest_month} "
        f"({monthly_average.loc[highest_month, 'mean']:.2f})"
    )

    print(
        f"Lowest average month: "
        f"{lowest_month} "
        f"({monthly_average.loc[lowest_month, 'mean']:.2f})"
    )

    GRAPH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        month_order,
        monthly_average["mean"],
        marker="o"
    )

    plt.title(
        "Average Monthly Seasonal Pattern "
        "of Food Products IIP"
    )

    plt.xlabel("Month")
    plt.ylabel("Average IIP Index")

    plt.xticks(rotation=45)

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = (
        GRAPH_DIR /
        "food_products_iip_monthly_seasonality.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nSeasonality graph saved to:\n"
        f"{output_file}"
    )
def analyze_annual_trend(df):
    print("\n" + "=" * 60)
    print("ANNUAL TREND ANALYSIS")
    print("=" * 60)

    annual_average = (
        df.groupby("year")["index"]
        .agg(["mean", "min", "max"])
    )

    print("\nAnnual IIP statistics:")
    print(annual_average.to_string())

    first_year_average = annual_average["mean"].iloc[0]
    last_year_average = annual_average["mean"].iloc[-1]

    percentage_change = (
        (last_year_average - first_year_average)
        / first_year_average
    ) * 100

    print(
        f"\nFirst-year average: "
        f"{first_year_average:.2f}"
    )

    print(
        f"Last-year average: "
        f"{last_year_average:.2f}"
    )

    print(
        f"Change across baseline period: "
        f"{percentage_change:.2f}%"
    )

    GRAPH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        annual_average.index,
        annual_average["mean"],
        marker="o"
    )

    plt.title(
        "Annual Average Food Products IIP"
    )

    plt.xlabel("Year")
    plt.ylabel("Average IIP Index")

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = (
        GRAPH_DIR /
        "food_products_iip_annual_trend.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nAnnual trend graph saved to:\n"
        f"{output_file}"
    )
def analyze_stationarity(df):
    print("\n" + "=" * 60)
    print("STATIONARITY ANALYSIS")
    print("=" * 60)

    from statsmodels.tsa.stattools import adfuller

    series = df["index"].dropna()

    result = adfuller(series)

    adf_statistic = result[0]
    p_value = result[1]
    used_lags = result[2]
    observations = result[3]

    print(f"\nADF Statistic: {adf_statistic:.6f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Used lags: {used_lags}")
    print(f"Number of observations: {observations}")

    print("\nCritical values:")

    for key, value in result[4].items():
        print(f"{key}: {value:.6f}")

    if p_value < 0.05:
        print("\nConclusion:")
        print("The original series is stationary at the 5% significance level.")
    else:
        print("\nConclusion:")
        print("The original series is non-stationary at the 5% significance level.")

def analyze_first_difference(df):
    print("\n" + "=" * 60)
    print("FIRST DIFFERENCE STATIONARITY ANALYSIS")
    print("=" * 60)

    from statsmodels.tsa.stattools import adfuller

    series = df["index"].dropna()

    first_difference = series.diff().dropna()

    result = adfuller(first_difference)

    adf_statistic = result[0]
    p_value = result[1]
    used_lags = result[2]
    observations = result[3]

    print("\nADF Test after first differencing:")

    print(f"ADF Statistic: {adf_statistic:.6f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Used lags: {used_lags}")
    print(f"Number of observations: {observations}")

    print("\nCritical values:")

    for key, value in result[4].items():
        print(f"{key}: {value:.6f}")

    if p_value < 0.05:
        print("\nConclusion:")
        print(
            "The first-differenced series is stationary "
            "at the 5% significance level."
        )
    else:
        print("\nConclusion:")
        print(
            "The first-differenced series is non-stationary "
            "at the 5% significance level."
        )

    GRAPH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["date"].iloc[1:],
        first_difference
    )

    plt.title(
        "First-Differenced Food Products IIP"
    )

    plt.xlabel("Date")
    plt.ylabel("First Difference")

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = (
        GRAPH_DIR /
        "food_products_iip_first_difference.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nFirst-difference graph saved to:\n"
        f"{output_file}"
    )
def analyze_seasonal_difference(df):
    print("\n" + "=" * 60)
    print("SEASONAL DIFFERENCE STATIONARITY ANALYSIS")
    print("=" * 60)

    from statsmodels.tsa.stattools import adfuller

    series = df["index"].dropna()

    seasonal_difference = series.diff(12).dropna()

    result = adfuller(seasonal_difference)

    adf_statistic = result[0]
    p_value = result[1]
    used_lags = result[2]
    observations = result[3]

    print("\nADF Test after seasonal differencing (lag 12):")

    print(f"ADF Statistic: {adf_statistic:.6f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Used lags: {used_lags}")
    print(f"Number of observations: {observations}")

    print("\nCritical values:")

    for key, value in result[4].items():
        print(f"{key}: {value:.6f}")

    if p_value < 0.05:
        print("\nConclusion:")
        print(
            "The seasonally differenced series is stationary "
            "at the 5% significance level."
        )
    else:
        print("\nConclusion:")
        print(
            "The seasonally differenced series is non-stationary "
            "at the 5% significance level."
        )

    GRAPH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["date"].iloc[12:],
        seasonal_difference
    )

    plt.title(
        "Seasonally Differenced Food Products IIP (Lag 12)"
    )

    plt.xlabel("Date")
    plt.ylabel("Seasonal Difference")

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = (
        GRAPH_DIR /
        "food_products_iip_seasonal_difference.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nSeasonal-difference graph saved to:\n"
        f"{output_file}"
    )
def analyze_combined_difference(df):
    print("\n" + "=" * 60)
    print("COMBINED DIFFERENCE STATIONARITY ANALYSIS")
    print("=" * 60)

    from statsmodels.tsa.stattools import adfuller

    series = df["index"].dropna()

    # First difference
    first_difference = series.diff()

    # Seasonal difference at lag 12
    combined_difference = first_difference.diff(12).dropna()

    result = adfuller(combined_difference)

    adf_statistic = result[0]
    p_value = result[1]
    used_lags = result[2]
    observations = result[3]

    print("\nADF Test after first + seasonal differencing:")

    print(f"ADF Statistic: {adf_statistic:.6f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Used lags: {used_lags}")
    print(f"Number of observations: {observations}")

    print("\nCritical values:")

    for key, value in result[4].items():
        print(f"{key}: {value:.6f}")

    if p_value < 0.05:
        print("\nConclusion:")
        print(
            "The combined-differenced series is stationary "
            "at the 5% significance level."
        )
    else:
        print("\nConclusion:")
        print(
            "The combined-differenced series is non-stationary "
            "at the 5% significance level."
        )

    GRAPH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["date"].iloc[13:],
        combined_difference
    )

    plt.title(
        "Food Products IIP - First + Seasonal Difference"
    )

    plt.xlabel("Date")
    plt.ylabel("Combined Difference")

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = (
        GRAPH_DIR /
        "food_products_iip_combined_difference.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nCombined-difference graph saved to:\n"
        f"{output_file}"
    )
def analyze_acf_pacf(df):
    print("\n" + "=" * 60)
    print("ACF AND PACF ANALYSIS")
    print("=" * 60)

    from statsmodels.tsa.stattools import acf, pacf

    series = df["index"].dropna()

    # First difference followed by seasonal difference at lag 12
    combined_difference = (
        series.diff().diff(12).dropna()
    )

    max_lags = 36

    acf_values = acf(
        combined_difference,
        nlags=max_lags
    )

    pacf_values = pacf(
        combined_difference,
        nlags=max_lags,
        method="ywm"
    )

    print("\nACF values at important lags:")

    for lag in [1, 2, 3, 12, 24, 36]:
        print(
            f"Lag {lag}: "
            f"{acf_values[lag]:.6f}"
        )

    print("\nPACF values at important lags:")

    for lag in [1, 2, 3, 12, 24, 36]:
        print(
            f"Lag {lag}: "
            f"{pacf_values[lag]:.6f}"
        )

    GRAPH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ACF plot
    from statsmodels.graphics.tsaplots import plot_acf

    plt.figure(figsize=(12, 6))

    plot_acf(
        combined_difference,
        lags=max_lags,
        ax=plt.gca()
    )

    plt.title(
        "ACF - Combined Differenced Food Products IIP"
    )

    plt.tight_layout()

    acf_file = (
        GRAPH_DIR /
        "food_products_iip_acf.png"
    )

    plt.savefig(
        acf_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # PACF plot
    from statsmodels.graphics.tsaplots import plot_pacf

    plt.figure(figsize=(12, 6))

    plot_pacf(
        combined_difference,
        lags=max_lags,
        ax=plt.gca(),
        method="ywm"
    )

    plt.title(
        "PACF - Combined Differenced Food Products IIP"
    )

    plt.tight_layout()

    pacf_file = (
        GRAPH_DIR /
        "food_products_iip_pacf.png"
    )

    plt.savefig(
        pacf_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nACF graph saved to:\n"
        f"{acf_file}"
    )

    print(
        f"\nPACF graph saved to:\n"
        f"{pacf_file}"
    )
def main():
    df = load_data()

    basic_analysis(df)

    create_time_series_plot(df)

    analyze_monthly_seasonality(df)

    analyze_annual_trend(df)

    analyze_stationarity(df)

    analyze_first_difference(df)

    analyze_seasonal_difference(df)

    analyze_combined_difference(df)

    analyze_acf_pacf(df)

    print("\n" + "=" * 60)
    print("EDA STEP 4 COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()