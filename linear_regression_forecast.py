from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


TRAIN_START = 2000
TRAIN_END = 2020
TEST_START = 2021
TEST_END = 2024

COUNTRY_CODE_DEFAULT = "TUR"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def calc_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """R² ve RMSE metriklerini hesaplar."""
    return {
        "R2": float(r2_score(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
    }


def load_sdmx_wb_csv(
    file_path: Path,
    country_code: str = COUNTRY_CODE_DEFAULT,
) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    required_cols = {"TIME_PERIOD", "OBS_VALUE", "REF_AREA", "INDICATOR"}
    missing_cols = sorted(required_cols.difference(df.columns))
    if missing_cols:
        raise ValueError(
            f"{file_path.name} SDMX formatında değil. Eksik sütunlar: {', '.join(missing_cols)}"
        )

    df_country = df[df["REF_AREA"] == country_code].copy()
    if df_country.empty:
        raise ValueError(f"{file_path.name} içinde {country_code} verisi yok.")

    df_country["Year"] = pd.to_numeric(df_country["TIME_PERIOD"], errors="coerce")
    df_country["Value"] = pd.to_numeric(df_country["OBS_VALUE"], errors="coerce")
    df_country = df_country.dropna(subset=["Year", "Value"])
    df_country["Year"] = df_country["Year"].astype(int)

    series = (
        df_country.groupby(["Year", "INDICATOR"], as_index=False)["Value"]
        .mean()
        .sort_values("Year")
    )
    label = (
        df_country["INDICATOR_LABEL"].dropna().iloc[0]
        if "INDICATOR_LABEL" in df_country.columns
        and not df_country["INDICATOR_LABEL"].dropna().empty
        else series["INDICATOR"].iloc[0]
    )
    series["Indicator_Label"] = label
    return series.reset_index(drop=True)


def train_predict_linear_regression(
    series_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float]]:
    if TRAIN_END >= TEST_START:
        raise ValueError("Eğitim ve test dönemleri çakışmamalıdır.")

    df = series_df.dropna(subset=["Value"]).copy()
    df = df[(df["Year"] >= TRAIN_START) & (df["Year"] <= TEST_END)]

    train_df = df[(df["Year"] >= TRAIN_START) & (df["Year"] <= TRAIN_END)]
    test_df = df[(df["Year"] >= TEST_START) & (df["Year"] <= TEST_END)]
    if train_df.empty:
        raise ValueError("Eğitim dönemi için kullanılabilir veri bulunamadı.")
    if len(test_df) < 2:
        raise ValueError("Metrik hesaplamak için test döneminde en az iki gözlem gerekir.")

    model = LinearRegression()
    model.fit(train_df[["Year"]].values, train_df["Value"].values)

    y_test = test_df["Value"].values
    y_pred = model.predict(test_df[["Year"]].values)
    metrics = calc_metrics(y_test, y_pred)

    pred_table = test_df[["Year"]].copy()
    pred_table["Actual"] = y_test
    pred_table["Predicted"] = y_pred
    pred_table["Error"] = y_pred - y_test
    return train_df, test_df, pred_table, metrics


def plot_forecast(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    pred_table: pd.DataFrame,
    title: str,
    out_path: Path,
) -> None:
    plt.figure(figsize=(11, 6))
    plt.plot(train_df["Year"], train_df["Value"], label="Train (Actual)", marker="o")
    plt.plot(test_df["Year"], test_df["Value"], label="Test (Actual)", marker="o")
    plt.plot(
        pred_table["Year"],
        pred_table["Predicted"],
        label="Test (Predicted)",
        linestyle="--",
        marker="o",
    )
    plt.xlabel("Year")
    plt.ylabel("Value")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    out_dir = base_dir / "output"
    ensure_dir(out_dir)

    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("data klasöründe CSV bulunamadı.")

    metrics_lines = [
        f"Train: {TRAIN_START}-{TRAIN_END}",
        f"Test : {TEST_START}-{TEST_END}",
        "",
    ]

    for csv_path in csv_files:
        series = load_sdmx_wb_csv(csv_path)
        indicator = series["Indicator_Label"].iloc[0]
        train_df, test_df, pred_table, metrics = train_predict_linear_regression(series)

        plot_forecast(
            train_df,
            test_df,
            pred_table,
            f"{indicator} - Linear Regression Forecast",
            out_dir / f"{csv_path.stem}_forecast.png",
        )
        pred_table.to_csv(out_dir / f"{csv_path.stem}_predictions.csv", index=False)

        metrics_lines.extend(
            [
                f"=== {csv_path.stem} ===",
                f"R2   : {metrics['R2']:.6f}",
                f"RMSE : {metrics['RMSE']:.6f}",
                "",
            ]
        )

    (out_dir / "metrics.txt").write_text("\n".join(metrics_lines), encoding="utf-8")
    print("Tüm işlemler tamamlandı. Çıktılar output/ klasöründe.")


if __name__ == "__main__":
    main()
