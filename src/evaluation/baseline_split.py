from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "iip_food_products_baseline_2012_2025.csv"
)


def create_baseline_split():
    print("=" * 60)
    print("BASELINE TRAIN/TEST SPLIT")
    print("=" * 60)

    df = pd.read_csv(DATA_FILE)

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    # Last 12 months are reserved for testing.
    test_size = 12

    train = df.iloc[:-test_size].copy()
    test = df.iloc[-test_size:].copy()

    print("\nComplete dataset:")
    print(f"Observations: {len(df)}")
    print(
        f"Date range: "
        f"{df['date'].min().date()} "
        f"to "
        f"{df['date'].max().date()}"
    )

    print("\nTraining dataset:")
    print(f"Observations: {len(train)}")
    print(
        f"Date range: "
        f"{train['date'].min().date()} "
        f"to "
        f"{train['date'].max().date()}"
    )

    print("\nTesting dataset:")
    print(f"Observations: {len(test)}")
    print(
        f"Date range: "
        f"{test['date'].min().date()} "
        f"to "
        f"{test['date'].max().date()}"
    )

    print("\nTest months:")
    print(
        test[
            ["date", "index"]
        ].to_string(index=False)
    )

    print("\nBaseline split verification:")

    expected_train_end = pd.Timestamp("2024-03-01")
    expected_test_start = pd.Timestamp("2024-04-01")
    expected_test_end = pd.Timestamp("2025-03-01")

    checks = {
        "Training observations = 144":
            len(train) == 144,

        "Test observations = 12":
            len(test) == 12,

        "Training ends March 2024":
            train["date"].max() == expected_train_end,

        "Testing starts April 2024":
            test["date"].min() == expected_test_start,

        "Testing ends March 2025":
            test["date"].max() == expected_test_end,

        "No missing training target":
            train["index"].isna().sum() == 0,

        "No missing testing target":
            test["index"].isna().sum() == 0,
    }

    all_passed = True

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"

        print(f"{status}: {check_name}")

        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("BASELINE SPLIT VERIFIED SUCCESSFULLY")
    else:
        print("BASELINE SPLIT VERIFICATION FAILED")

    print("=" * 60)


if __name__ == "__main__":
    create_baseline_split()