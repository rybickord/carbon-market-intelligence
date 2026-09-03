"""
Company carbon-trading decision classifier.

Target: Target_Trade_Action
In this processed dataset the target is exactly Buy (1) vs Sell (0);
Transaction_Type maps 1:1 onto the label and is excluded as leakage.
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

RAW_DATA_PATH = processed_dir() / "company_trading_dataset.csv"
MODELS_DIR = models_dir() / "company_trading"
EVAL_PATH = processed_dir() / "company_trading_evaluation.json"
DOCS_PATH = docs_dir() / "company_trading_model.md"
TARGET_COL = "Target_Trade_Action"

EXCLUDED_COLS = [
    "Company_ID",
    "Date",
    "Optimization_Scenario",
    "Carbon_Cost_Savings_USD",
    "Transaction_Type",
    "Credits_Traded_tCO2",
    TARGET_COL,
]

CATEGORICAL_COLS = ["Industry_Type", "Fuel_Type", "Verification_Status"]
NUMERIC_COLS = [
    "Energy_Demand_MWh",
    "Emission_Produced_tCO2",
    "Emission_Allowance_tCO2",
    "Carbon_Price_USD_per_t",
    "Compliance_Cost_USD",
]
DERIVED_COLS = ["Allowance_Gap_tCO2"]

LEAKAGE_AUDIT = [
    {
        "column": "Transaction_Type",
        "decision": "exclude",
        "reason": "In the processed file Buy maps exactly to Target_Trade_Action=1 and Sell to 0. Using it would reconstruct the label.",
    },
    {
        "column": "Carbon_Cost_Savings_USD",
        "decision": "exclude",
        "reason": "Recorded cost savings are an outcome of the executed action, not a pre-decision input.",
    },
    {
        "column": "Optimization_Scenario",
        "decision": "exclude",
        "reason": "Scenario tag describes the case after the optimization/trade framing; it is not a firm-state variable available as a trading input.",
    },
    {
        "column": "Credits_Traded_tCO2",
        "decision": "exclude",
        "reason": "This is the volume of the transaction that was executed. It is known only after the decision to buy or sell.",
    },
    {
        "column": "Company_ID",
        "decision": "exclude",
        "reason": "Identifier. It would allow memorizing firms rather than learning transferable drivers.",
    },
    {
        "column": "Date",
        "decision": "exclude",
        "reason": "Calendar stamp is not a causal pre-trade feature and can leak period-specific artifacts.",
    },
    {
        "column": "Compliance_Cost_USD",
        "decision": "include",
        "reason": "Treated as a known compliance obligation cost available before the trade. Means are similar across classes, so it is not a disguised label.",
    },
    {
        "column": "Verification_Status",
        "decision": "include",
        "reason": "Compliance/verification state of the firm can be known before a trade is placed.",
    },
]


def load_and_validate(data_path: Path | None = None):
    path = Path(data_path) if data_path else RAW_DATA_PATH
    df = pd.read_csv(path)
    print(f"\nLoaded: {path}  shape={df.shape}")
    print(f"Target distribution:\n{df[TARGET_COL].value_counts().to_string()}")
    print(f"\nNaN counts:\n{df.isnull().sum().to_string()}")

    expected = set(EXCLUDED_COLS + CATEGORICAL_COLS + NUMERIC_COLS)
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Expected columns not found: {missing}")

    work = df.copy()
    work["Allowance_Gap_tCO2"] = (
        work["Emission_Produced_tCO2"] - work["Emission_Allowance_tCO2"]
    )
    feature_cols = CATEGORICAL_COLS + NUMERIC_COLS + DERIVED_COLS
    X = work[feature_cols].copy()
    y = work[TARGET_COL].copy()

    print(f"\nFeature set ({len(feature_cols)} columns): {feature_cols}")
    print("Excluded columns (leakage/identifier):")
    for col in [c for c in EXCLUDED_COLS if c != TARGET_COL]:
        print(f"  {col}")
    return X, y, df


def build_preprocessor():
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    return ColumnTransformer(
        [
            (
                "cat",
                Pipeline(
                    [
                        (
                            "ohe",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        )
                    ]
                ),
                CATEGORICAL_COLS,
            ),
            (
                "num",
                Pipeline([("scaler", StandardScaler())]),
                NUMERIC_COLS + DERIVED_COLS,
            ),
        ]
    )


def compute_metrics(y_true, y_pred, y_prob=None):
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    metrics = {
        "Accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "Precision": round(
            float(precision_score(y_true, y_pred, average="binary", zero_division=0)), 4
        ),
        "Recall": round(
            float(recall_score(y_true, y_pred, average="binary", zero_division=0)), 4
        ),
        "F1": round(float(f1_score(y_true, y_pred, average="binary", zero_division=0)), 4),
        "Precision_weighted": round(
            float(precision_score(y_true, y_pred, average="weighted", zero_division=0)), 4
        ),
        "Recall_weighted": round(
            float(recall_score(y_true, y_pred, average="weighted", zero_division=0)), 4
        ),
        "F1_weighted": round(
            float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4
        ),
    }
    if y_prob is not None:
        metrics["ROC_AUC"] = round(float(roc_auc_score(y_true, y_prob)), 4)
    metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()
    return metrics


def get_feature_names(preprocessor) -> list:
    cat_names = list(
        preprocessor.named_transformers_["cat"]["ohe"].get_feature_names_out(
            CATEGORICAL_COLS
        )
    )
    return cat_names + NUMERIC_COLS + DERIVED_COLS


def get_feature_importance(model, feature_names: list, model_name: str) -> dict:
    if model_name == "LogisticRegression":
        importance = {
            f: round(float(c), 6) for f, c in zip(feature_names, model.coef_[0])
        }
    elif hasattr(model, "feature_importances_"):
        importance = {
            f: round(float(v), 6)
            for f, v in zip(feature_names, model.feature_importances_)
        }
    else:
        return {}
    return dict(sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)[:20])


def _model_factory():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42, n_jobs=1),
        "RandomForest": RandomForestClassifier(
            n_estimators=150, max_depth=8, random_state=42, n_jobs=1
        ),
    }
    try:
        import xgboost as xgb

        models["XGBoost"] = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            n_jobs=1,
            verbosity=0,
            eval_metric="logloss",
            tree_method="hist",
        )
    except ImportError:
        pass
    return models


def train_and_evaluate(X, y):
    from sklearn.model_selection import StratifiedShuffleSplit

    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(sss.split(X, y))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    print(f"\nTrain size: {len(X_train)}  |  Test size: {len(X_test)}", flush=True)
    print(f"Train target dist: {y_train.value_counts().to_dict()}", flush=True)
    print(f"Test  target dist: {y_test.value_counts().to_dict()}", flush=True)

    preprocessor = build_preprocessor()
    X_train_t = preprocessor.fit_transform(X_train)
    X_test_t = preprocessor.transform(X_test)
    feature_names = get_feature_names(preprocessor)

    results = {}
    for name, model in _model_factory().items():
        print(f"\n  Training {name}...", flush=True)
        model.fit(X_train_t, y_train)
        y_pred = model.predict(X_test_t)
        y_prob = model.predict_proba(X_test_t)[:, 1] if hasattr(model, "predict_proba") else None
        metrics = compute_metrics(y_test, y_pred, y_prob)
        fi = get_feature_importance(model, feature_names, name)
        print(
            f"    Accuracy={metrics['Accuracy']}  F1={metrics['F1']}  "
            f"AUC={metrics.get('ROC_AUC', 'N/A')}",
            flush=True,
        )
        results[name] = {"model": model, "metrics": metrics, "feature_importance": fi}

    return results, preprocessor, feature_names, {
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "train_balance": {str(k): int(v) for k, v in y_train.value_counts().items()},
        "test_balance": {str(k): int(v) for k, v in y_test.value_counts().items()},
        "full_balance": {str(k): int(v) for k, v in y.value_counts().items()},
    }


def select_best_model(results: dict) -> str:
    best = max(results, key=lambda n: results[n]["metrics"]["F1"])
    print(f"\n  Selected best model: {best} (F1={results[best]['metrics']['F1']})")
    return best


def save_artifacts(results, preprocessor, feature_names, selected_name, split_info, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "classifier.pkl"
    preprocessor_path = output_dir / "preprocessor.pkl"
    joblib.dump(results[selected_name]["model"], model_path)
    joblib.dump(preprocessor, preprocessor_path)

    all_metrics = {
        name: {k: v for k, v in res["metrics"].items()}
        for name, res in results.items()
    }
    metadata = {
        "target": TARGET_COL,
        "target_interpretation": "1 = Buy, 0 = Sell (matches Transaction_Type in source file)",
        "selected_model": selected_name,
        "validation": "stratified 80/20 train/test split, random_state=42",
        "excluded_columns": [c for c in EXCLUDED_COLS if c != TARGET_COL],
        "categorical_features": CATEGORICAL_COLS,
        "numeric_features": NUMERIC_COLS,
        "derived_features": DERIVED_COLS,
        "feature_names_after_preprocessing": feature_names,
        "all_model_metrics": {
            name: {k: v for k, v in mets.items() if k != "confusion_matrix"}
            for name, mets in all_metrics.items()
        },
        "selected_model_metrics": results[selected_name]["metrics"],
        "feature_importance_top20": results[selected_name]["feature_importance"],
        "class_balance": split_info,
        "leakage_audit": LEAKAGE_AUDIT,
        "model_path": str(model_path.as_posix()),
        "preprocessor_path": str(preprocessor_path.as_posix()),
        "input_fields": CATEGORICAL_COLS + NUMERIC_COLS,
    }
    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    processed_dir().mkdir(parents=True, exist_ok=True)
    with open(EVAL_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "selected_model": selected_name,
                "metrics": results[selected_name]["metrics"],
                "all_model_metrics": all_metrics,
                "class_balance": split_info,
                "excluded_columns": metadata["excluded_columns"],
            },
            f,
            indent=2,
        )
    print(f"\n  Artifacts saved to: {output_dir}")
    return metadata


def write_docs(metadata: dict):
    docs_dir().mkdir(parents=True, exist_ok=True)
    lines = [
        "# Company Trading Decision Model",
        "",
        "## Target",
        "",
        f"`{TARGET_COL}` is binary. In the processed dataset it is identical to the",
        "Buy/Sell flag: 1 = Buy, 0 = Sell. There is no 'no trade' class in this file.",
        "",
        "## Leakage audit",
        "",
        "| Column | Decision | Reason |",
        "|---|---|---|",
    ]
    for item in LEAKAGE_AUDIT:
        lines.append(f"| `{item['column']}` | {item['decision']} | {item['reason']} |")
    lines.extend(
        [
            "",
            "## Included features",
            "",
            "- Categorical: " + ", ".join(f"`{c}`" for c in CATEGORICAL_COLS),
            "- Numeric: " + ", ".join(f"`{c}`" for c in NUMERIC_COLS),
            "- Derived (pre-decision): `Allowance_Gap_tCO2` = emissions minus allowance",
            "",
            "## Validation",
            "",
            metadata["validation"],
            "",
            f"Class balance (full file): {metadata['class_balance']['full_balance']}",
            "",
            "## Models",
            "",
            "Logistic regression baseline, random forest, and XGBoost when available.",
            "Selection criterion is binary F1 on the held-out test set, not accuracy alone.",
            "",
            f"Selected model: **{metadata['selected_model']}**",
            "",
            "## Test metrics",
            "",
            "| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name, m in metadata["all_model_metrics"].items():
        lines.append(
            f"| {name} | {m.get('Accuracy')} | {m.get('Precision')} | "
            f"{m.get('Recall')} | {m.get('F1')} | {m.get('ROC_AUC')} |"
        )
    cm = metadata["selected_model_metrics"]["confusion_matrix"]
    lines.extend(
        [
            "",
            "Selected-model confusion matrix (rows = actual 0/1, columns = predicted 0/1):",
            "",
            f"`{cm}`",
            "",
            "## Limitations",
            "",
            "- The label is a reconstructed Buy/Sell action, not an observed future decision.",
            "- Predictive power depends on whether allowance gaps and costs actually drive trades in this table.",
            "- Company identifiers were excluded, so firm-specific trading style is not modeled.",
            "- Probabilities are classifier scores on a held-out split, not calibrated market odds.",
            "",
            "## Outputs",
            "",
            "- `ml/models/company_trading/`",
            "- `data/processed/company_trading_evaluation.json`",
            "",
        ]
    )
    DOCS_PATH.write_text("\n".join(lines), encoding="utf-8")


def predict(input_data, models_dir=None):
    models_dir = Path(models_dir) if models_dir else MODELS_DIR
    with open(models_dir / "metadata.json", encoding="utf-8") as f:
        meta = json.load(f)
    model = joblib.load(meta["model_path"] if Path(meta["model_path"]).exists() else models_dir / "classifier.pkl")
    preprocessor = joblib.load(
        meta["preprocessor_path"]
        if Path(meta.get("preprocessor_path", "")).exists()
        else models_dir / "preprocessor.pkl"
    )
    row = pd.DataFrame([input_data])
    if "Allowance_Gap_tCO2" not in row.columns:
        row["Allowance_Gap_tCO2"] = (
            row["Emission_Produced_tCO2"] - row["Emission_Allowance_tCO2"]
        )
    X_t = preprocessor.transform(row)
    pred = int(model.predict(X_t)[0])
    prob = float(model.predict_proba(X_t)[0][1]) if hasattr(model, "predict_proba") else None
    label = "Buy" if pred == 1 else "Sell"
    return {
        "prediction": pred,
        "predicted_action": label,
        "probability_buy": prob,
        "model_name": meta["selected_model"],
    }


def main(data_path=None, output_dir=None):
    os.chdir(project_root())
    print("=" * 60)
    print("COMPANY TRADING CLASSIFIER - MODEL TRAINING")
    print("=" * 60)
    X, y, _ = load_and_validate(data_path)
    results, preprocessor, feature_names, split_info = train_and_evaluate(X, y)
    selected_name = select_best_model(results)
    meta = save_artifacts(
        results,
        preprocessor,
        feature_names,
        selected_name,
        split_info,
        output_dir or MODELS_DIR,
    )
    write_docs(meta)
    print("\nTRAINING COMPLETE")
    return meta


if __name__ == "__main__":
    main()
