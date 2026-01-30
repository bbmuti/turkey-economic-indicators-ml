import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error


TRAIN_START = 2000
TRAIN_END   = 2020
TEST_START  = 2020
TEST_END    = 2024

COUNTRY_CODE_DEFAULT = "TUR"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return np.nan

def calc_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Sadece R² ve RMSE"""
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return {
        "R2": r2,
        "RMSE": rmse
    }

def load_sdmx_wb_csv(file_path: Path, country_code: str = COUNTRY_CODE_DEFAULT) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    required_cols = {"TIME_PERIOD", "OBS_VALUE", "REF_AREA", "INDICATOR"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"{file_path.name} SDMX formatında değil.")

    df_country = df[df["REF_AREA"] == country_code].copy()
    if df_country.empty:
        raise ValueError(f"{file_path.name} içinde {country_code} verisi yok.")

    df_country["Year"] = df_country["TIME_PERIOD"].astype(int)
    df_country["Value"] = df_country["OBS_VALUE"].apply(safe_float)

    df_country = (
        df_country
        .groupby(["Year", "INDICATOR"], as_index=False)["Value"]
        .mean()
        .sort_values("Year")
    )

    df_country["Indicator_Label"] = (
        df["INDICATOR_LABEL"].iloc[0]
        if "INDICATOR_LABEL" in df.columns
        else df_country["INDICATOR"].iloc[0]
    )

    return df_country.reset_index(drop=True)

def train_predict_linear_regression(series_df: pd.DataFrame) -> dict:
    df = series_df.dropna(subset=["Value"]).copy()
    df = df[(df["Year"] >= TRAIN_START) & (df["Year"] <= TEST_END)]

    train_df = df[(df["Year"] >= TRAIN_START) & (df["Year"] <= TRAIN_END)]
    test_df  = df[(df["Year"] >= TEST_START) & (df["Year"] <= TEST_END)]

    X_train = train_df[["Year"]].values
    y_train = train_df["Value"].values

    X_test = test_df[["Year"]].values
    y_test = test_df["Value"].values

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = calc_metrics(y_test, y_pred)

    pred_table = test_df[["Year"]].copy()
    pred_table["Actual"] = y_test
    pred_table["Predicted"] = y_pred
    pred_table["Error"] = y_pred - y_test

    return train_df, test_df, pred_table, metrics

def plot_forecast(train_df, test_df, pred_table, title, out_path):
    plt.figure(figsize=(11, 6))
    plt.plot(train_df["Year"], train_df["Value"], label="Train (Actual)", marker="o")
    plt.plot(test_df["Year"], test_df["Value"], label="Test (Actual)", marker="o")
    plt.plot(pred_table["Year"], pred_table["Predicted"],
             label="Test (Predicted)", linestyle="--", marker="o")

    plt.xlabel("Year")
    plt.ylabel("Value")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    out_dir = base_dir / "output"
    ensure_dir(out_dir)

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("data klasöründe CSV bulunamadı.")

    metrics_lines = []
    metrics_lines.append(f"Train: {TRAIN_START}-{TRAIN_END}")
    metrics_lines.append(f"Test : {TEST_START}-{TEST_END}")
    metrics_lines.append("")

    for csv_path in csv_files:
        series = load_sdmx_wb_csv(csv_path)
        indicator = series["Indicator_Label"].iloc[0]

        train_df, test_df, pred_table, metrics = train_predict_linear_regression(series)

        stem = csv_path.stem

        plot_path = out_dir / f"{stem}_forecast.png"
        table_path = out_dir / f"{stem}_predictions.csv"

        plot_forecast(
            train_df,
            test_df,
            pred_table,
            f"{indicator} - Linear Regression Forecast",
            plot_path
        )

        pred_table.to_csv(table_path, index=False)

        metrics_lines.append(f"=== {stem} ===")
        metrics_lines.append(f"R2   : {metrics['R2']:.6f}")
        metrics_lines.append(f"RMSE : {metrics['RMSE']:.6f}")
        metrics_lines.append("")

    with open(out_dir / "metrics.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(metrics_lines))

    print("Tüm işlemler tamamlandı. Çıktılar output/ klasöründe.")


if __name__ == "__main__":
    main()