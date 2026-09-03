"""
Global carbon-market forecasting.

Dataset: data/processed/global_market_timeseries.csv (annual, 2005–2024).
Targets: Market_Value, Market_Volume (both present in the processed file).

Validation: expanding-window walk-forward (no random split).
Leakage controls: lag/rolling features use shift(1)+; macros are lagged one year.
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

for _var in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[_var] = "1"

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ml.paths import docs_dir, models_dir, processed_dir, project_root

RAW_DATA_PATH = processed_dir() / "global_market_timeseries.csv"
MODELS_DIR = models_dir() / "global_market"
FORECAST_PATH = processed_dir() / "global_market_forecast.csv"
WALKFORWARD_PATH = processed_dir() / "global_market_walkforward.csv"
METRICS_PATH = processed_dir() / "global_market_model_metrics.json"
DOCS_PATH = docs_dir() / "global_market_forecasting.md"

MIN_TRAIN_SIZE = 12
HORIZON_YEARS = 3
TARGET_COLS = ["Market_Value", "Market_Volume"]
MACRO_COLS = [
    "Global_CO2",
    "Renewable_Electricity_Share",
    "Renewable_Production",
    "Global_GDP_Growth",
]


def load_series(data_path: Path | None = None) -> pd.DataFrame:
    path = Path(data_path) if data_path else RAW_DATA_PATH
    df = pd.read_csv(path)
    df = df.sort_values("Year").drop_duplicates(subset=["Year"]).reset_index(drop=True)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Lag/rolling features only. Macros are shifted so year t uses year t-1 values."""
    df = df.copy().sort_values("Year").reset_index(drop=True)
    df["Year_Index"] = df["Year"] - df["Year"].min()

    for target in TARGET_COLS:
        df[f"{target}_lag1"] = df[target].shift(1)
        df[f"{target}_lag2"] = df[target].shift(2)
        df[f"{target}_roll3"] = (
            df[target].shift(1).rolling(window=3, min_periods=2).mean()
        )
        prev = df[target].shift(1)
        prev2 = df[target].shift(2)
        df[f"{target}_growth"] = (prev - prev2) / prev2.replace(0, np.nan)

    for col in MACRO_COLS:
        if col in df.columns:
            # Last-known carry-forward, then lag one year so same-year macros are unused.
            df[f"{col}_lag1"] = df[col].ffill().shift(1)

    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    cols = ["Year_Index"]
    for target in TARGET_COLS:
        for suffix in ["_lag1", "_lag2", "_roll3", "_growth"]:
            name = f"{target}{suffix}"
            if name in df.columns:
                cols.append(name)
    for col in MACRO_COLS:
        lagged = f"{col}_lag1"
        if lagged in df.columns:
            cols.append(lagged)
    return [c for c in cols if c in df.columns]


def compute_metrics(y_true, y_pred) -> dict:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else float("nan")
    if np.all(y_true != 0):
        mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)
    else:
        mape = None
    return {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "R2": None if np.isnan(r2) else round(r2, 4),
        "MAPE": None if mape is None else round(mape, 4),
        "n": int(len(y_true)),
    }


def _model_factory():
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression

    cfg = {
        "LinearRegression": lambda: LinearRegression(),
        "RandomForest": lambda: RandomForestRegressor(
            n_estimators=80, max_depth=2, min_samples_leaf=2, random_state=42, n_jobs=1
        ),
    }
    try:
        import xgboost as xgb

        cfg["XGBoost"] = lambda: xgb.XGBRegressor(
            n_estimators=40,
            max_depth=2,
            learning_rate=0.1,
            random_state=42,
            n_jobs=1,
            verbosity=0,
            tree_method="hist",
        )
    except ImportError:
        pass
    return cfg


def walk_forward_cv(df_feat: pd.DataFrame, feature_cols: list[str], target: str, min_train: int):
    from sklearn.preprocessing import StandardScaler

    needed = feature_cols + [target, "Year"]
    df = df_feat.dropna(subset=needed).reset_index(drop=True)
    n = len(df)
    if n <= min_train:
        raise ValueError(
            f"Insufficient complete rows ({n}) for walk-forward CV (min={min_train})."
        )

    print(
        f"  Walk-forward CV: {n} complete rows, {min_train} initial train, "
        f"{n - min_train} test steps",
        flush=True,
    )

    results = {}
    years = []
    naive_preds, ma_preds, actuals = [], [], []
    for t in range(min_train, n):
        years.append(int(df["Year"].iloc[t]))
        actuals.append(float(df[target].iloc[t]))
        naive_preds.append(float(df[target].iloc[t - 1]))
        window = df[target].iloc[max(0, t - 3) : t]
        ma_preds.append(float(window.mean()))

    results["Naive_LastValue"] = {
        "years": years,
        "preds": naive_preds,
        "actuals": actuals,
        "metrics": compute_metrics(actuals, naive_preds),
    }
    results["MovingAverage_3"] = {
        "years": years,
        "preds": ma_preds,
        "actuals": actuals,
        "metrics": compute_metrics(actuals, ma_preds),
    }

    for name, model_fn in _model_factory().items():
        print(f"  CV: {name}...", flush=True)
        preds = []
        for t in range(min_train, n):
            train = df.iloc[:t]
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(train[feature_cols].values)
            y_tr = train[target].values
            X_te = scaler.transform(df.iloc[t : t + 1][feature_cols].values)
            model = model_fn()
            model.fit(X_tr, y_tr)
            preds.append(float(model.predict(X_te)[0]))
        results[name] = {
            "years": years,
            "preds": preds,
            "actuals": actuals,
            "metrics": compute_metrics(actuals, preds),
        }
        m = results[name]["metrics"]
        print(
            f"    {name}: MAE={m['MAE']} RMSE={m['RMSE']} R2={m['R2']} MAPE={m['MAPE']}",
            flush=True,
        )
    return results, df


def select_and_train_final(df_feat, feature_cols, target, wf_results):
    from sklearn.preprocessing import StandardScaler

    rmse_scores = {n: r["metrics"]["RMSE"] for n, r in wf_results.items()}
    best_name = min(rmse_scores, key=rmse_scores.get)
    print(f"  Lowest walk-forward RMSE: {best_name} ({rmse_scores[best_name]:.4f})", flush=True)

    if best_name in ("Naive_LastValue", "MovingAverage_3"):
        return None, None, best_name

    df = df_feat.dropna(subset=feature_cols + [target]).reset_index(drop=True)
    scaler = StandardScaler()
    X_s = scaler.fit_transform(df[feature_cols].values)
    y = df[target].values
    model = _model_factory()[best_name]()
    model.fit(X_s, y)
    return model, scaler, best_name


def get_feature_importance(model, feature_cols, model_name):
    if model is None:
        return {}
    if model_name == "LinearRegression":
        return dict(zip(feature_cols, [round(float(c), 6) for c in model.coef_]))
    if hasattr(model, "feature_importances_"):
        return dict(
            zip(feature_cols, [round(float(v), 6) for v in model.feature_importances_])
        )
    return {}


def _last_complete_feature_row(df_feat: pd.DataFrame, feature_cols: list[str]) -> dict:
    complete = df_feat.dropna(subset=feature_cols)
    if complete.empty:
        raise ValueError("No complete feature rows available for forecasting.")
    row = complete.iloc[-1]
    return {c: float(row[c]) for c in feature_cols}


def forecast_horizon(df: pd.DataFrame, target: str, meta: dict, horizon: int = HORIZON_YEARS):
    """Recursive next-step forecasts. Macros are held at last known lagged values."""
    df_feat = build_features(df)
    feature_cols = meta["feature_columns"]
    selected = meta["selected_model"]
    last_year = int(df["Year"].max())
    last_value = float(df[target].iloc[-1])
    prev_value = float(df[target].iloc[-2]) if len(df) > 1 else last_value

    history = df[["Year", target]].copy()
    preds = []

    if selected == "Naive_LastValue":
        for i in range(1, horizon + 1):
            preds.append({"Year": last_year + i, target: last_value, "model": selected})
        return preds

    if selected == "MovingAverage_3":
        window = list(df[target].iloc[-3:].astype(float))
        for i in range(1, horizon + 1):
            value = float(np.mean(window[-3:]))
            preds.append({"Year": last_year + i, target: value, "model": selected})
            window.append(value)
        return preds

    model = joblib.load(meta["model_path"])
    scaler = joblib.load(meta["scaler_path"])
    features = _last_complete_feature_row(df_feat, feature_cols)
    lag1, lag2 = last_value, prev_value
    roll_hist = list(df[target].iloc[-3:].astype(float))

    for i in range(1, horizon + 1):
        year = last_year + i
        features["Year_Index"] = float(year - int(df["Year"].min()))
        features[f"{target}_lag1"] = lag1
        features[f"{target}_lag2"] = lag2
        features[f"{target}_roll3"] = float(np.mean(roll_hist[-3:])) if roll_hist else lag1
        features[f"{target}_growth"] = (lag1 - lag2) / lag2 if lag2 else 0.0
        row = np.array([[features.get(c, np.nan) for c in feature_cols]], dtype=float)
        value = float(model.predict(scaler.transform(row))[0])
        preds.append({"Year": year, target: value, "model": selected})
        lag2, lag1 = lag1, value
        roll_hist.append(value)

    _ = history
    return preds


def predict(target: str, last_known_values: dict, models_dir: Path | str | None = None) -> float:
    models_dir = Path(models_dir) if models_dir else MODELS_DIR
    safe_target = target.lower().replace(" ", "_")
    with open(models_dir / f"{safe_target}_metadata.json", encoding="utf-8") as f:
        meta = json.load(f)
    selected = meta["selected_model"]
    if selected == "Naive_LastValue":
        return float(last_known_values.get(f"{target}_lag1", np.nan))
    if selected == "MovingAverage_3":
        roll = last_known_values.get(f"{target}_roll3")
        if roll is not None:
            return float(roll)
        return float(last_known_values.get(f"{target}_lag1", np.nan))
    model = joblib.load(meta["model_path"])
    scaler = joblib.load(meta["scaler_path"])
    row = np.array([[last_known_values.get(c, np.nan) for c in meta["feature_columns"]]])
    return float(model.predict(scaler.transform(row))[0])


def save_artifacts(target, model, scaler, selected_name, feature_cols, wf_results, df, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_target = target.lower().replace(" ", "_")
    years = sorted(df["Year"].dropna().astype(int).tolist())
    metadata = {
        "target": target,
        "selected_model": selected_name,
        "feature_columns": feature_cols,
        "validation": "expanding-window walk-forward (chronological)",
        "min_train_size": MIN_TRAIN_SIZE,
        "training_period": {"start_year": years[0], "end_year": years[-1]},
        "frequency": "annual",
        "n_observations": int(len(df)),
        "walk_forward_metrics": {n: r["metrics"] for n, r in wf_results.items()},
        "training_rows": int(
            build_features(df).dropna(subset=feature_cols + [target]).shape[0]
        ),
        "horizon_years": HORIZON_YEARS,
        "leakage_controls": [
            "No random train/test split",
            "Lag and rolling statistics use shift(1) or greater",
            "Macro indicators are lagged one year after last-known forward-fill",
            "Walk-forward trains only on years strictly before the test year",
        ],
    }
    if model is not None:
        model_path = output_dir / f"{safe_target}_model.pkl"
        scaler_path = output_dir / f"{safe_target}_scaler.pkl"
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        metadata["model_path"] = str(model_path.as_posix())
        metadata["scaler_path"] = str(scaler_path.as_posix())
        metadata["feature_importance"] = get_feature_importance(
            model, feature_cols, selected_name
        )
    meta_path = output_dir / f"{safe_target}_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Artifacts saved: {output_dir}", flush=True)
    return metadata


def write_forecast_outputs(df: pd.DataFrame, all_meta: dict, all_wf: dict):
    processed_dir().mkdir(parents=True, exist_ok=True)
    forecast_rows = []
    for _, row in df.iterrows():
        rec = {
            "Year": int(row["Year"]),
            "Market_Value": float(row["Market_Value"]),
            "Market_Volume": float(row["Market_Volume"]),
            "Series": "historical",
        }
        forecast_rows.append(rec)

    future_by_year: dict[int, dict] = {}
    for target, meta in all_meta.items():
        for item in forecast_horizon(df, target, meta, HORIZON_YEARS):
            year = int(item["Year"])
            future_by_year.setdefault(year, {"Year": year, "Series": "forecast"})
            future_by_year[year][target] = float(item[target])
            future_by_year[year][f"{target}_model"] = item["model"]
    forecast_rows.extend(future_by_year[y] for y in sorted(future_by_year))
    forecast_df = pd.DataFrame(forecast_rows)
    forecast_df.to_csv(FORECAST_PATH, index=False)

    wf_rows = []
    for target, wf in all_wf.items():
        selected = all_meta[target]["selected_model"]
        block = wf[selected]
        for year, actual, pred in zip(block["years"], block["actuals"], block["preds"]):
            wf_rows.append(
                {
                    "Year": year,
                    "Target": target,
                    "Actual": actual,
                    "Predicted": pred,
                    "Model": selected,
                    "Split": "walk_forward",
                }
            )
    pd.DataFrame(wf_rows).to_csv(WALKFORWARD_PATH, index=False)

    metrics_payload = {
        target: {
            "selected_model": all_meta[target]["selected_model"],
            "walk_forward_metrics": all_meta[target]["walk_forward_metrics"],
        }
        for target in all_meta
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)
    return forecast_df


def write_docs(all_meta: dict):
    docs_dir().mkdir(parents=True, exist_ok=True)
    lines = [
        "# Global Carbon Market Forecasting",
        "",
        "## Dataset",
        "",
        "- Source: `data/processed/global_market_timeseries.csv`",
        "- Frequency: annual",
        "- Range: 2005–2024 (20 observations)",
        "- Targets present and used: `Market_Value`, `Market_Volume`",
        "",
        "## Why this setup is small-sample",
        "",
        "Twenty annual points is a short series. Complex models can overfit easily.",
        "Walk-forward RMSE is therefore compared against naive last-value and a 3-year",
        "moving-average baseline. If a machine-learning model does not improve RMSE,",
        "the simpler method is selected.",
        "",
        "## Features",
        "",
        "Built only from information available before the predicted year:",
        "",
        "- `Year_Index` (time trend)",
        "- Lag-1, lag-2, 3-year rolling mean, and lag growth for both market series",
        "- One-year lags of `Global_CO2`, `Renewable_Electricity_Share`,",
        "  `Renewable_Production`, and `Global_GDP_Growth`",
        "",
        "Missing 2022–2024 CO2/renewable fields are forward-filled from the last known",
        "year and then lagged, so they represent last known values, not fabricated fills",
        "for the same year as the target.",
        "",
        "## Validation",
        "",
        "Expanding-window walk-forward: initial training window is the first 12 complete",
        "rows; each later year is predicted using only earlier years.",
        "",
        "## Models compared",
        "",
        "- Naive last-value",
        "- 3-year moving average",
        "- Linear regression",
        "- Random forest (shallow trees)",
        "- XGBoost (if installed; shallow trees)",
        "",
        "## Results",
        "",
    ]
    for target, meta in all_meta.items():
        lines.append(f"### {target}")
        lines.append("")
        lines.append(f"- Selected model: **{meta['selected_model']}**")
        lines.append("")
        lines.append("| Model | MAE | RMSE | R² | MAPE | n |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for name, m in meta["walk_forward_metrics"].items():
            r2 = m.get("R2")
            mape = m.get("MAPE")
            lines.append(
                f"| {name} | {m['MAE']} | {m['RMSE']} | {r2} | {mape} | {m.get('n', '')} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Leakage prevention",
            "",
            "- Chronological walk-forward only",
            "- No contemporaneous macros for the target year",
            "- No random shuffle",
            "- Recursive multi-year forecasts hold macros at last known lagged values",
            "",
            "## Limitations",
            "",
            "- Annual series with 20 points; uncertainty is high",
            "- 2021 value/volume spike dominates recent error",
            "- R² can be negative when a persistent-level forecast misses a structural jump",
            "- Forward forecasts are not guaranteed outcomes",
            "- Macro coverage ends in 2021 for CO2 and renewables",
            "",
            "## Outputs",
            "",
            "- Models/metadata: `ml/models/global_market/`",
            "- Combined history + forecast: `data/processed/global_market_forecast.csv`",
            "- Walk-forward predictions: `data/processed/global_market_walkforward.csv`",
            "- Metrics JSON: `data/processed/global_market_model_metrics.json`",
            "",
        ]
    )
    DOCS_PATH.write_text("\n".join(lines), encoding="utf-8")


def run_target(target, data_path=None, output_dir=None):
    data_path = Path(data_path) if data_path else RAW_DATA_PATH
    output_dir = Path(output_dir) if output_dir else MODELS_DIR
    print(f"\n{'=' * 60}", flush=True)
    print(f"GLOBAL MARKET FORECASTING: {target}", flush=True)
    print(f"{'=' * 60}", flush=True)

    os.chdir(project_root())
    df = load_series(data_path)
    print(f"Loaded: {data_path} shape={df.shape}", flush=True)
    df_feat = build_features(df)
    feature_cols = get_feature_columns(df_feat)
    print(f"Features ({len(feature_cols)}): {feature_cols}", flush=True)

    wf_results, _ = walk_forward_cv(df_feat, feature_cols, target, MIN_TRAIN_SIZE)
    print(f"\nWalk-forward summary for {target}:", flush=True)
    for name, res in wf_results.items():
        m = res["metrics"]
        print(
            f"  {name:<22} MAE={m['MAE']} RMSE={m['RMSE']} R2={m['R2']} MAPE={m['MAPE']}",
            flush=True,
        )

    model, scaler, selected_name = select_and_train_final(
        df_feat, feature_cols, target, wf_results
    )
    meta = save_artifacts(
        target, model, scaler, selected_name, feature_cols, wf_results, df, output_dir
    )
    print(f"DONE: {target}", flush=True)
    return meta, wf_results, df


def main(data_path=None, output_dir=None):
    os.chdir(project_root())
    all_results = {}
    all_wf = {}
    df = None
    for target in TARGET_COLS:
        meta, wf, df = run_target(target, data_path, output_dir)
        all_results[target] = meta
        all_wf[target] = wf
    write_forecast_outputs(df, all_results, all_wf)
    write_docs(all_results)
    return all_results


if __name__ == "__main__":
    sys.path.insert(0, str(project_root()))
    target_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if target_arg:
        run_target(target_arg)
    else:
        main()
