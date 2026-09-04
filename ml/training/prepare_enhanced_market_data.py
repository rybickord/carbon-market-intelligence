"""
Enhanced global market data preparation integrating new carbon and energy datasets.

This script creates an ENHANCED version of global_market_timeseries.csv that includes:
1. Existing: Market Value, Market Volume, CO2, Renewables, GDP
2. NEW: Carbon Price, Carbon Volume (contracts), Oil/Gas/Coal prices

Purpose: Test whether new features improve forecasting performance.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import sys

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from ml.paths import processed_dir

RAW_DIR = Path("data/raw")
PROCESSED_DIR = processed_dir()

# Input files
MASTER_FILE = RAW_DIR / "carbon_and_energy_master_2000_2026.xlsx"
EXISTING_TIMESERIES = PROCESSED_DIR / "global_market_timeseries.csv"

# Output files
OUTPUT_ENHANCED = PROCESSED_DIR / "global_market_timeseries_enhanced.csv"
OUTPUT_BASELINE = PROCESSED_DIR / "global_market_timeseries_baseline.csv"


def load_master_dataset():
    """Load the carbon and energy master dataset (daily data)."""
    print("\nLoading carbon_and_energy_master_2000_2026.xlsx...")
    df = pd.read_excel(MASTER_FILE, sheet_name="Master Dataset")
    
    print(f"  Rows: {len(df)}")
    print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"  Columns: {list(df.columns)}")
    
    # Parse date
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    
    # Count missing carbon prices by year
    missing_by_year = df.groupby('Year')['Carbon_Price_EUR_Tonne'].apply(lambda x: x.isnull().sum())
    print(f"\n  Missing carbon prices by year (sample):")
    print(missing_by_year.head(10))
    
    return df


def aggregate_to_annual(df_daily):
    """
    Aggregate daily carbon and energy data to annual frequency.
    
    Key decisions:
    - Carbon_Price: mean of available prices (only exists from Phase I onward)
    - Carbon_Volume: sum of daily contracts
    - Oil/Gas/Coal: mean annual prices
    - Market_Phase: most common phase in the year
    """
    print("\nAggregating daily data to annual...")
    
    # Group by year
    annual = df_daily.groupby('Year').agg({
        'Carbon_Price_EUR_Tonne': 'mean',  # Mean price (NaN for pre-market years)
        'Carbon_Volume_Contracts': 'sum',  # Total volume
        'Brent_Crude_USD_Barrel': 'mean',
        'Dutch_TTF_Gas_EUR_MWh': 'mean',
        'API2_Coal_USD_Metric_Tonne': 'mean',
        'Market_Phase': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown'
    }).reset_index()
    
    # Rename for clarity
    annual.rename(columns={
        'Carbon_Price_EUR_Tonne': 'Carbon_Price_EUR_Annual_Mean',
        'Carbon_Volume_Contracts': 'Carbon_Volume_Contracts_Annual_Sum',
        'Brent_Crude_USD_Barrel': 'Oil_Price_USD_Annual_Mean',
        'Dutch_TTF_Gas_EUR_MWh': 'Gas_Price_EUR_Annual_Mean',
        'API2_Coal_USD_Metric_Tonne': 'Coal_Price_USD_Annual_Mean',
    }, inplace=True)
    
    print(f"  Annual rows: {len(annual)}")
    print(f"  Year range: {annual['Year'].min()} to {annual['Year'].max()}")
    
    return annual


def load_existing_timeseries():
    """Load existing processed timeseries with macro features."""
    print("\nLoading existing global_market_timeseries.csv...")
    df = pd.read_csv(EXISTING_TIMESERIES)
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    return df


def merge_datasets(existing, annual_new):
    """
    Merge existing timeseries with new annual carbon/energy data.
    
    The existing dataset covers 2005-2024.
    The new dataset covers 2000-2026 but only has carbon prices from ~2005 onward.
    """
    print("\nMerging datasets...")
    
    # Merge on Year
    merged = pd.merge(existing, annual_new, on='Year', how='left')
    
    print(f"  Merged rows: {len(merged)}")
    print(f"  Columns after merge: {list(merged.columns)}")
    
    # Check coverage
    print(f"\n  Carbon price coverage:")
    print(f"    Non-null: {merged['Carbon_Price_EUR_Annual_Mean'].notna().sum()} / {len(merged)}")
    print(f"    Years with carbon price: {merged[merged['Carbon_Price_EUR_Annual_Mean'].notna()]['Year'].min()} - {merged[merged['Carbon_Price_EUR_Annual_Mean'].notna()]['Year'].max()}")
    
    return merged


def create_baseline_copy():
    """Create a copy of the existing timeseries as baseline for comparison."""
    print("\nCreating baseline copy...")
    existing = load_existing_timeseries()
    existing.to_csv(OUTPUT_BASELINE, index=False)
    print(f"  Saved: {OUTPUT_BASELINE}")
    return existing


def save_enhanced(df):
    """Save the enhanced dataset."""
    print(f"\nSaving enhanced dataset...")
    df.to_csv(OUTPUT_ENHANCED, index=False)
    print(f"  Saved: {OUTPUT_ENHANCED}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")


def generate_summary():
    """Generate summary of what was created."""
    print("\n" + "="*80)
    print("DATA PREPARATION COMPLETE")
    print("="*80)
    
    print("\n[BASELINE]")
    print(f"  File: {OUTPUT_BASELINE}")
    print("  Description: Copy of existing global_market_timeseries.csv (Phase 3 baseline)")
    print("  Features: Market_Value, Market_Volume, CO2, Renewables, GDP")
    print("  Years: 2005-2024 (20 years)")
    
    print("\n[ENHANCED]")
    print(f"  File: {OUTPUT_ENHANCED}")
    print("  Description: Baseline + new carbon price/volume + energy prices")
    print("  Features: All baseline features PLUS:")
    print("    - Carbon_Price_EUR_Annual_Mean")
    print("    - Carbon_Volume_Contracts_Annual_Sum")
    print("    - Oil_Price_USD_Annual_Mean")
    print("    - Gas_Price_EUR_Annual_Mean")
    print("    - Coal_Price_USD_Annual_Mean")
    print("    - Market_Phase")
    print("  Years: 2005-2024 (20 years, aligned with baseline)")
    
    print("\n[NEXT STEP]")
    print("  Run: python ml/training/compare_market_models.py")
    print("  This will train models on BASELINE vs ENHANCED and compare performance.")


def main():
    """Main data preparation pipeline."""
    print("="*80)
    print("ENHANCED GLOBAL MARKET DATA PREPARATION")
    print("="*80)
    
    # Step 1: Create baseline copy
    baseline = create_baseline_copy()
    
    # Step 2: Load new master dataset
    df_daily = load_master_dataset()
    
    # Step 3: Aggregate to annual
    annual_new = aggregate_to_annual(df_daily)
    
    # Step 4: Merge with existing
    enhanced = merge_datasets(baseline, annual_new)
    
    # Step 5: Save enhanced dataset
    save_enhanced(enhanced)
    
    # Step 6: Summary
    generate_summary()


if __name__ == "__main__":
    main()
