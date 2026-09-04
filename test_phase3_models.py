"""
Quick validation script to ensure Phase 3 models can be loaded.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import joblib
import json
import pandas as pd

def test_company_trading_model():
    print("Testing Company Trading Model...")
    models_dir = ROOT / "ml" / "models" / "company_trading"
    
    with open(models_dir / "metadata.json") as f:
        meta = json.load(f)
    
    model = joblib.load(models_dir / "classifier.pkl")
    preprocessor = joblib.load(models_dir / "preprocessor.pkl")
    
    print(f"  Selected model: {meta['selected_model']}")
    print(f"  Input fields: {meta['input_fields']}")
    print(f"  F1 Score: {meta['selected_model_metrics']['F1']}")
    print(f"  ROC-AUC: {meta['selected_model_metrics']['ROC_AUC']}")
    print("  ✓ Company trading model loaded successfully\n")
    return True

def test_global_market_model():
    print("Testing Global Market Model...")
    models_dir = ROOT / "ml" / "models" / "global_market"
    
    # Check Market_Value
    with open(models_dir / "market_value_metadata.json") as f:
        value_meta = json.load(f)
    print(f"  Market_Value selected: {value_meta['selected_model']}")
    print(f"  Market_Value RMSE: {value_meta['walk_forward_metrics'][value_meta['selected_model']]['RMSE']}")
    
    # Check Market_Volume
    with open(models_dir / "market_volume_metadata.json") as f:
        volume_meta = json.load(f)
    print(f"  Market_Volume selected: {volume_meta['selected_model']}")
    print(f"  Market_Volume RMSE: {volume_meta['walk_forward_metrics'][volume_meta['selected_model']]['RMSE']}")
    
    # Try loading XGBoost model if it exists
    if volume_meta['selected_model'] == 'XGBoost':
        model = joblib.load(models_dir / "market_volume_model.pkl")
        scaler = joblib.load(models_dir / "market_volume_scaler.pkl")
        print("  ✓ XGBoost model and scaler loaded successfully")
    
    print("  ✓ Global market models validated\n")
    return True

def test_processed_data():
    print("Testing Processed Data Files...")
    data_dir = ROOT / "data" / "processed"
    
    files = [
        "global_market_forecast.csv",
        "global_market_walkforward.csv",
        "global_market_model_metrics.json",
        "company_trading_evaluation.json",
        "country_risk_scores.csv",
        "country_opportunity_scores.csv"
    ]
    
    for fname in files:
        fpath = data_dir / fname
        if not fpath.exists():
            print(f"  ✗ Missing: {fname}")
            return False
        
        if fname.endswith('.csv'):
            df = pd.read_csv(fpath)
            print(f"  ✓ {fname}: {df.shape[0]} rows")
        else:
            with open(fpath) as f:
                data = json.load(f)
            print(f"  ✓ {fname}: loaded")
    
    print()
    return True

if __name__ == "__main__":
    try:
        test_company_trading_model()
        test_global_market_model()
        test_processed_data()
        print("="*60)
        print("✓ Phase 3 validation PASSED")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Phase 3 validation FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
