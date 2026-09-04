"""
Controlled comparison of baseline vs enhanced global market forecasting models.

MODEL 1 (BASELINE): Existing Phase 3 features only
MODEL 2 (CARBON ONLY): Baseline + carbon price/volume features
MODEL 3 (CARBON + ENERGY): Baseline + carbon + energy prices
MODEL 4 (FULL ENHANCED): All available features

Validation: Walk-forward cross-validation (chronological, no leakage)
Decision: Select model with best performance; keep baseline if new features don't help
"""

from pathlib import Path
import pandas as pd
import numpy as np
import sys
import json
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from ml.paths import processed_dir, models_dir

BASELINE_FILE = processed_dir() / "global_market_timeseries_baseline.csv"
ENHANCED_FILE = processed_dir() / "global_market_timeseries_enhanced.csv"
OUTPUT_COMPARISON = processed_dir() / "model_comparison_results.json"

MIN_TRAIN = 12
TARGET_COLS = ["Market_Value", "Market_Volume"]


def load_data(filepath):
    """Load and sort timeseries data."""
    df = pd.read_csv(filepath)
    df = df.sort_values('Year').reset_index(drop=True)
    return df


def build_baseline_features(df):
    """Build features matching Phase 3 baseline exactly."""
    df = df.copy().sort_values('Year').reset_index(drop=True)
    df['Year_Index'] = df['Year'] - df['Year'].min()
    
    # Lag/rolling features for targets
    for target in TARGET_COLS:
        df[f'{target}_lag1'] = df[target].shift(1)
        df[f'{target}_lag2'] = df[target].shift(2)
        df[f'{target}_roll3'] = df[target].shift(1).rolling(window=3, min_periods=2).mean()
        prev = df[target].shift(1)
        prev2 = df[target].shift(2)
        df[f'{target}_growth'] = (prev - prev2) / prev2.replace(0, np.nan)
    
    # Macro features (lagged)
    for col in ['Global_CO2', 'Renewable_Electricity_Share', 'Renewable_Production', 'Global_GDP_Growth']:
        if col in df.columns:
            df[f'{col}_lag1'] = df[col].ffill().shift(1)
    
    feature_cols = ['Year_Index']
    for target in TARGET_COLS:
        for suffix in ['_lag1', '_lag2', '_roll3', '_growth']:
            name = f'{target}{suffix}'
            if name in df.columns:
                feature_cols.append(name)
    
    for col in ['Global_CO2', 'Renewable_Electricity_Share', 'Renewable_Production', 'Global_GDP_Growth']:
        lagged = f'{col}_lag1'
        if lagged in df.columns:
            feature_cols.append(lagged)
    
    return df, [c for c in feature_cols if c in df.columns]


def build_carbon_features(df):
    """Add carbon price and volume features to baseline."""
    df, baseline_features = build_baseline_features(df)
    
    # Carbon price features (lagged to prevent leakage)
    if 'Carbon_Price_EUR_Annual_Mean' in df.columns:
        df['Carbon_Price_lag1'] = df['Carbon_Price_EUR_Annual_Mean'].shift(1)
        df['Carbon_Price_lag2'] = df['Carbon_Price_EUR_Annual_Mean'].shift(2)
        df['Carbon_Price_roll3'] = df['Carbon_Price_EUR_Annual_Mean'].shift(1).rolling(window=3, min_periods=2).mean()
        prev_price = df['Carbon_Price_EUR_Annual_Mean'].shift(1)
        prev2_price = df['Carbon_Price_EUR_Annual_Mean'].shift(2)
        df['Carbon_Price_return'] = (prev_price - prev2_price) / prev2_price.replace(0, np.nan)
        
        baseline_features.extend(['Carbon_Price_lag1', 'Carbon_Price_lag2', 'Carbon_Price_roll3', 'Carbon_Price_return'])
    
    # Carbon volume features (lagged)
    if 'Carbon_Volume_Contracts_Annual_Sum' in df.columns:
        df['Carbon_Volume_lag1'] = df['Carbon_Volume_Contracts_Annual_Sum'].shift(1)
        df['Carbon_Volume_growth'] = df['Carbon_Volume_Contracts_Annual_Sum'].pct_change().shift(1)
        
        baseline_features.extend(['Carbon_Volume_lag1', 'Carbon_Volume_growth'])
    
    return df, [c for c in baseline_features if c in df.columns]


def build_energy_features(df):
    """Add energy price features to carbon features."""
    df, carbon_features = build_carbon_features(df)
    
    # Energy price features (lagged)
    for energy_col in ['Oil_Price_USD_Annual_Mean', 'Gas_Price_EUR_Annual_Mean', 'Coal_Price_USD_Annual_Mean']:
        if energy_col in df.columns:
            df[f'{energy_col}_lag1'] = df[energy_col].shift(1)
            df[f'{energy_col}_return'] = df[energy_col].pct_change().shift(1)
            carbon_features.extend([f'{energy_col}_lag1', f'{energy_col}_return'])
    
    return df, [c for c in carbon_features if c in df.columns]


def build_full_features(df):
    """All available features."""
    return build_energy_features(df)


def naive_forecast(df, target):
    """Simple last-value baseline for comparison."""
    df = df.copy()
    df[f'{target}_naive'] = df[target].shift(1)
    return df


def compute_metrics(y_true, y_pred):
    """Compute evaluation metrics."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true = y_true[mask]
    y_pred = y_pred[mask]
    
    if len(y_true) == 0:
        return {'MAE': None, 'RMSE': None, 'R2': None, 'MAPE': None, 'n': 0}
    
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred)) if len(y_true) >= 2 else None
    
    if np.all(y_true != 0):
        mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)
    else:
        mape = None
    
    return {
        'MAE': round(mae, 4),
        'RMSE': round(rmse, 4),
        'R2': round(r2, 4) if r2 is not None else None,
        'MAPE': round(mape, 4) if mape is not None else None,
        'n': int(len(y_true))
    }


def walk_forward_cv(df, feature_cols, target, model_name='XGBoost'):
    """Walk-forward cross-validation."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    
    try:
        import xgboost as xgb
        has_xgb = True
    except ImportError:
        has_xgb = False
    
    predictions = []
    actuals = []
    
    for i in range(MIN_TRAIN, len(df)):
        train_df = df.iloc[:i]
        test_df = df.iloc[i:i+1]
        
        # Filter complete rows
        train_complete = train_df.dropna(subset=feature_cols + [target])
        test_complete = test_df.dropna(subset=feature_cols + [target])
        
        if len(train_complete) < MIN_TRAIN or len(test_complete) == 0:
            continue
        
        X_train = train_complete[feature_cols].values
        y_train = train_complete[target].values
        X_test = test_complete[feature_cols].values
        y_test = test_complete[target].values
        
        # Scale
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_name == 'XGBoost' and has_xgb:
            model = xgb.XGBRegressor(n_estimators=40, max_depth=2, learning_rate=0.1, random_state=42, n_jobs=1, verbosity=0)
        elif model_name == 'RandomForest':
            model = RandomForestRegressor(n_estimators=80, max_depth=2, min_samples_leaf=2, random_state=42, n_jobs=1)
        else:
            model = LinearRegression()
        
        model.fit(X_train_scaled, y_train)
        pred = model.predict(X_test_scaled)[0]
        
        predictions.append(pred)
        actuals.append(y_test[0])
    
    metrics = compute_metrics(actuals, predictions)
    return metrics, predictions, actuals


def evaluate_naive_baseline(df, target):
    """Evaluate naive last-value forecast."""
    df = naive_forecast(df, target)
    df_test = df[MIN_TRAIN:].copy()
    
    y_true = df_test[target].values
    y_pred = df_test[f'{target}_naive'].values
    
    return compute_metrics(y_true, y_pred)


def run_model_comparison(target):
    """Run complete model comparison for one target."""
    print(f"\n{'='*80}")
    print(f"TARGET: {target}")
    print('='*80)
    
    results = {'target': target, 'models': {}}
    
    # Load data
    baseline_df = load_data(BASELINE_FILE)
    enhanced_df = load_data(ENHANCED_FILE)
    
    # Naive baseline
    print("\n[NAIVE BASELINE]")
    naive_metrics = evaluate_naive_baseline(baseline_df, target)
    print(f"  RMSE: {naive_metrics['RMSE']}, MAPE: {naive_metrics['MAPE']}%")
    results['models']['Naive_LastValue'] = naive_metrics
    
    # Model 1: Phase 3 Baseline
    print("\n[MODEL 1: BASELINE]")
    df1, features1 = build_baseline_features(baseline_df)
    print(f"  Features: {len(features1)}")
    m1_metrics, _, _ = walk_forward_cv(df1, features1, target)
    print(f"  RMSE: {m1_metrics['RMSE']}, MAPE: {m1_metrics['MAPE']}%")
    results['models']['Baseline_XGBoost'] = m1_metrics
    results['models']['Baseline_XGBoost']['features'] = features1
    
    # Model 2: Baseline + Carbon
    print("\n[MODEL 2: BASELINE + CARBON]")
    df2, features2 = build_carbon_features(enhanced_df)
    print(f"  Features: {len(features2)}")
    m2_metrics, _, _ = walk_forward_cv(df2, features2, target)
    print(f"  RMSE: {m2_metrics['RMSE']}, MAPE: {m2_metrics['MAPE']}%")
    results['models']['Carbon_XGBoost'] = m2_metrics
    results['models']['Carbon_XGBoost']['features'] = features2
    
    # Model 3: Baseline + Carbon + Energy
    print("\n[MODEL 3: BASELINE + CARBON + ENERGY]")
    df3, features3 = build_energy_features(enhanced_df)
    print(f"  Features: {len(features3)}")
    m3_metrics, _, _ = walk_forward_cv(df3, features3, target)
    print(f"  RMSE: {m3_metrics['RMSE']}, MAPE: {m3_metrics['MAPE']}%")
    results['models']['Full_Enhanced_XGBoost'] = m3_metrics
    results['models']['Full_Enhanced_XGBoost']['features'] = features3
    
    # Compare
    print("\n[COMPARISON]")
    print(f"  Naive:    RMSE={naive_metrics['RMSE']:.4f}, MAPE={naive_metrics.get('MAPE', 'N/A')}")
    print(f"  Baseline: RMSE={m1_metrics['RMSE']:.4f}, MAPE={m1_metrics.get('MAPE', 'N/A')}")
    print(f"  +Carbon:  RMSE={m2_metrics['RMSE']:.4f}, MAPE={m2_metrics.get('MAPE', 'N/A')}")
    print(f"  +Energy:  RMSE={m3_metrics['RMSE']:.4f}, MAPE={m3_metrics.get('MAPE', 'N/A')}")
    
    # Determine winner
    rmse_scores = {
        'Naive': naive_metrics['RMSE'],
        'Baseline': m1_metrics['RMSE'],
        'Carbon': m2_metrics['RMSE'],
        'Full': m3_metrics['RMSE']
    }
    winner = min(rmse_scores, key=rmse_scores.get)
    print(f"\n  WINNER: {winner} (lowest RMSE)")
    results['winner'] = winner
    
    return results


def main():
    """Run full comparison experiment."""
    print("="*80)
    print("GLOBAL MARKET MODEL COMPARISON EXPERIMENT")
    print("="*80)
    
    all_results = {}
    
    for target in TARGET_COLS:
        results = run_model_comparison(target)
        all_results[target] = results
    
    # Save results
    with open(OUTPUT_COMPARISON, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("EXPERIMENT COMPLETE")
    print('='*80)
    print(f"\nResults saved: {OUTPUT_COMPARISON}")
    
    # Summary
    print("\n[SUMMARY]")
    for target in TARGET_COLS:
        winner = all_results[target]['winner']
        print(f"  {target}: {winner}")
    
    print("\n[DECISION]")
    print("  Next step: Retrain selected model and update Phase 3 artifacts")
    print("  If new features don't improve: KEEP baseline (honest reporting)")


if __name__ == "__main__":
    main()
