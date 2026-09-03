"""
Master build script for Phase 3.
Run from any directory:

    ./venv/Scripts/python.exe -u ml/training/build_phase3.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for var in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[var] = "1"

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
os.chdir(_ROOT)

import numpy as np
import pandas as pd
import joblib

from ml.paths import docs_dir, models_dir, processed_dir, project_root
from ml.training.company_trading_model import main as train_company
from ml.training.global_market_model import main as train_global
from ml.training.risk_opportunity_engine import main as run_risk_opp
import ml.training.company_trading_model as ctm
import ml.training.global_market_model as gmm


def validate_global_model():
    print("\n-- Validating Global Model --")
    data_path = processed_dir() / "global_market_timeseries.csv"
    models = models_dir() / "global_market"
    for target in ["Market_Value", "Market_Volume"]:
        safe = target.lower().replace(" ", "_")
        meta_path = models / f"{safe}_metadata.json"
        assert meta_path.exists(), f"Missing {meta_path}"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"  {target}: selected_model={meta['selected_model']}")
        for model_name, m in meta["walk_forward_metrics"].items():
            print(
                f"    {model_name:<22} MAE={m['MAE']} RMSE={m['RMSE']} "
                f"R2={m['R2']} MAPE={m['MAPE']}"
            )
        selected = meta["selected_model"]
        if selected not in ("Naive_LastValue", "MovingAverage_3"):
            model = joblib.load(meta["model_path"])
            scaler = joblib.load(meta["scaler_path"])
            assert model is not None and scaler is not None
        df = pd.read_csv(data_path)
        df_feat = gmm.build_features(df)
        feat_cols = gmm.get_feature_columns(df_feat)
        last_row = df_feat.dropna(subset=feat_cols).iloc[-1]
        test_input = {c: float(last_row[c]) for c in feat_cols}
        pred = gmm.predict(target, test_input, models)
        assert pred is not None and not (isinstance(pred, float) and np.isnan(pred))
        print(f"    predict() -> {pred:.2f}")
    for fname in [
        "global_market_forecast.csv",
        "global_market_walkforward.csv",
        "global_market_model_metrics.json",
    ]:
        path = processed_dir() / fname
        assert path.exists(), f"Missing {path}"
        if fname.endswith(".csv"):
            out = pd.read_csv(path)
            numeric = out.select_dtypes(include=[np.number])
            assert not np.isinf(numeric.to_numpy()).any()
    print("  Global model validation PASSED")


def validate_company_model():
    print("\n-- Validating Company Classifier --")
    models = models_dir() / "company_trading"
    meta = json.loads((models / "metadata.json").read_text(encoding="utf-8"))
    print(f"  Selected model: {meta['selected_model']}")
    print(f"  Test metrics: {meta['selected_model_metrics']}")
    model = joblib.load(models / "classifier.pkl")
    preprocessor = joblib.load(models / "preprocessor.pkl")
    assert model is not None and preprocessor is not None
    sample = {
        "Industry_Type": "Manufacturing",
        "Energy_Demand_MWh": 5000.0,
        "Fuel_Type": "Natural Gas",
        "Emission_Produced_tCO2": 2500.0,
        "Emission_Allowance_tCO2": 2000.0,
        "Carbon_Price_USD_per_t": 25.0,
        "Compliance_Cost_USD": 12500.0,
        "Verification_Status": "Verified",
    }
    result = ctm.predict(sample, models)
    assert result["prediction"] in (0, 1)
    assert 0.0 <= result["probability_buy"] <= 1.0
    eval_path = processed_dir() / "company_trading_evaluation.json"
    assert eval_path.exists()
    print(f"  predict() -> {result}")
    print("  Company model validation PASSED")


def validate_scores():
    print("\n-- Validating Risk & Opportunity Scores --")
    for fname, score_col in [
        ("country_risk_scores.csv", "Risk_Score"),
        ("country_opportunity_scores.csv", "Opportunity_Score"),
    ]:
        path = processed_dir() / fname
        assert path.exists(), f"Missing {path}"
        df = pd.read_csv(path)
        assert df[score_col].between(0, 100).all()
        assert not df[score_col].isna().any()
        print(f"  {fname}: {len(df)} rows, [{df[score_col].min():.2f}, {df[score_col].max():.2f}]")
    print("  Score validation PASSED")


def write_phase3_results():
    global_meta = {}
    for target in ["market_value", "market_volume"]:
        path = models_dir() / "global_market" / f"{target}_metadata.json"
        global_meta[target] = json.loads(path.read_text(encoding="utf-8"))
    company = json.loads(
        (models_dir() / "company_trading" / "metadata.json").read_text(encoding="utf-8")
    )
    risk = pd.read_csv(processed_dir() / "country_risk_scores.csv")
    opp = pd.read_csv(processed_dir() / "country_opportunity_scores.csv")
    docs_dir().mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 3 Results",
        "",
        "Generated by `ml/training/build_phase3.py` after a real training run.",
        "Metrics below are written from saved artifacts, not hand-entered.",
        "",
        "## Global forecasting",
        "",
    ]
    for key, meta in global_meta.items():
        lines.append(f"### {meta['target']}")
        lines.append("")
        lines.append(f"- Selected: `{meta['selected_model']}`")
        lines.append(f"- Validation: {meta['validation']}")
        lines.append(f"- Training period: {meta['training_period']}")
        lines.append("")
        lines.append("| Model | MAE | RMSE | R² | MAPE |")
        lines.append("|---|---:|---:|---:|---:|")
        for name, m in meta["walk_forward_metrics"].items():
            lines.append(
                f"| {name} | {m['MAE']} | {m['RMSE']} | {m.get('R2')} | {m.get('MAPE')} |"
            )
        lines.append("")
    cm = company["selected_model_metrics"]
    lines.extend(
        [
            "## Company trading classifier",
            "",
            f"- Selected: `{company['selected_model']}`",
            f"- Validation: {company['validation']}",
            f"- Excluded: {', '.join(company['excluded_columns'])}",
            "",
            f"- Accuracy: {cm['Accuracy']}",
            f"- Precision: {cm.get('Precision')}",
            f"- Recall: {cm.get('Recall')}",
            f"- F1: {cm.get('F1')}",
            f"- ROC-AUC: {cm.get('ROC_AUC')}",
            f"- Confusion matrix: `{cm['confusion_matrix']}`",
            "",
            "## Country scores",
            "",
            f"- Risk rows: {len(risk)}; range {risk['Risk_Score'].min():.2f}–{risk['Risk_Score'].max():.2f}",
            f"- Opportunity rows: {len(opp)}; range {opp['Opportunity_Score'].min():.2f}–{opp['Opportunity_Score'].max():.2f}",
            "",
            "## Validation checks",
            "",
            "- Models reload with joblib",
            "- Forecast and evaluation files exist",
            "- Scores are finite and inside 0–100",
            "- Scripts resolve paths from the repository root",
            "",
            "## Limitations carried forward",
            "",
            "- Global series has only 20 annual points",
            "- Trading label is Buy/Sell reconstructed from Transaction_Type",
            "- Country scores are relative ranks on latest available year (through 2021)",
            "",
        ]
    )
    (docs_dir() / "phase3_results.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("\n" + "=" * 70)
    print("PHASE 3 - MASTER BUILD")
    print("=" * 70)
    train_global()
    train_company()
    run_risk_opp()
    validate_global_model()
    validate_company_model()
    validate_scores()
    write_phase3_results()
    print("\nALL PHASE 3 BUILD STEPS COMPLETE")


if __name__ == "__main__":
    main()
