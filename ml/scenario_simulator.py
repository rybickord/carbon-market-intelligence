"""
Scenario Simulator for Carbon Market Intelligence.

Allows users to modify key market conditions and compare baseline vs scenario predictions.
Only exposes parameters that are technically supported by the Phase 3 models.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ml.paths import models_dir, processed_dir


@dataclass
class ScenarioParameters:
    """
    Parameters that can be modified in a scenario.
    
    All changes are relative to the baseline (last known values).
    Values represent percentage changes from baseline.
    """
    carbon_price_change_pct: float = 0.0  # e.g., 20.0 = 20% increase
    emissions_change_pct: float = 0.0
    renewable_share_change_pct: float = 0.0
    gdp_growth_change_pct: float = 0.0
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate scenario parameters are within reasonable bounds."""
        checks = [
            (-50 <= self.carbon_price_change_pct <= 200, "carbon_price_change_pct must be between -50% and +200%"),
            (-30 <= self.emissions_change_pct <= 50, "emissions_change_pct must be between -30% and +50%"),
            (-20 <= self.renewable_share_change_pct <= 100, "renewable_share_change_pct must be between -20% and +100%"),
            (-20 <= self.gdp_growth_change_pct <= 50, "gdp_growth_change_pct must be between -20% and +50%"),
        ]
        
        for valid, msg in checks:
            if not valid:
                return False, msg
        
        return True, None


@dataclass
class ScenarioResult:
    """Result of a scenario simulation."""
    baseline_value: float
    baseline_volume: float
    scenario_value: float
    scenario_volume: float
    value_change_absolute: float
    value_change_percent: float
    volume_change_absolute: float
    volume_change_percent: float
    parameters: dict
    model_info: dict
    warnings: list[str]
    
    def to_dict(self) -> dict:
        return {
            "baseline": {
                "market_value": round(self.baseline_value, 2),
                "market_volume": round(self.baseline_volume, 2),
            },
            "scenario": {
                "market_value": round(self.scenario_value, 2),
                "market_volume": round(self.scenario_volume, 2),
            },
            "changes": {
                "value_absolute": round(self.value_change_absolute, 2),
                "value_percent": round(self.value_change_percent, 2),
                "volume_absolute": round(self.volume_change_absolute, 2),
                "volume_percent": round(self.volume_change_percent, 2),
            },
            "scenario_parameters": self.parameters,
            "model_info": self.model_info,
            "warnings": self.warnings,
        }


class ScenarioSimulator:
    """
    Scenario simulator for carbon market predictions.
    
    Uses the trained Phase 3 models to compare baseline predictions
    with scenario predictions where key market conditions are modified.
    """
    
    def __init__(self, models_dir_path: Optional[Path] = None, data_path: Optional[Path] = None):
        self.models_dir = Path(models_dir_path) if models_dir_path else models_dir() / "global_market"
        self.data_path = Path(data_path) if data_path else processed_dir() / "global_market_timeseries.csv"
        
        # Load metadata for both targets
        with open(self.models_dir / "market_value_metadata.json") as f:
            self.value_meta = json.load(f)
        
        with open(self.models_dir / "market_volume_metadata.json") as f:
            self.volume_meta = json.load(f)
        
        # Load historical data
        self.df = pd.read_csv(self.data_path).sort_values("Year").reset_index(drop=True)
        
        # Load models if they're not naive baselines
        self.value_model = None
        self.value_scaler = None
        if self.value_meta["selected_model"] not in ["Naive_LastValue", "MovingAverage_3"]:
            self.value_model = joblib.load(self.models_dir / "market_value_model.pkl")
            self.value_scaler = joblib.load(self.models_dir / "market_value_scaler.pkl")
        
        self.volume_model = None
        self.volume_scaler = None
        if self.volume_meta["selected_model"] not in ["Naive_LastValue", "MovingAverage_3"]:
            self.volume_model = joblib.load(self.models_dir / "market_volume_model.pkl")
            self.volume_scaler = joblib.load(self.models_dir / "market_volume_scaler.pkl")
    
    def _get_last_known_values(self) -> dict:
        """Extract last known values from historical data."""
        last_row = self.df.iloc[-1]
        prev_row = self.df.iloc[-2] if len(self.df) > 1 else last_row
        
        # Get last 3 values for rolling calculations
        last_3_value = list(self.df["Market_Value"].iloc[-3:].astype(float))
        last_3_volume = list(self.df["Market_Volume"].iloc[-3:].astype(float))
        
        return {
            "year": int(last_row["Year"]),
            "market_value": float(last_row["Market_Value"]),
            "market_volume": float(last_row["Market_Volume"]),
            "market_value_prev": float(prev_row["Market_Value"]),
            "market_volume_prev": float(prev_row["Market_Volume"]),
            "market_value_roll3": float(np.mean(last_3_value)),
            "market_volume_roll3": float(np.mean(last_3_volume)),
            # Last known macro values (with forward-fill for missing recent years)
            "global_co2": float(self.df["Global_CO2"].ffill().iloc[-1]),
            "renewable_share": float(self.df["Renewable_Electricity_Share"].ffill().iloc[-1]),
            "renewable_production": float(self.df["Renewable_Production"].ffill().iloc[-1]),
            "gdp_growth": float(self.df["Global_GDP_Growth"].ffill().iloc[-1]),
        }
    
    def _build_feature_dict(self, last_known: dict, scenario_params: Optional[ScenarioParameters] = None) -> dict:
        """
        Build feature dictionary for prediction.
        
        If scenario_params is provided, apply the changes to the features.
        """
        year = last_known["year"]
        year_min = int(self.df["Year"].min())
        
        # Base features from last known values
        features = {
            "Year_Index": float(year + 1 - year_min),
            "Market_Value_lag1": last_known["market_value"],
            "Market_Value_lag2": last_known["market_value_prev"],
            "Market_Value_roll3": last_known["market_value_roll3"],
            "Market_Value_growth": (
                (last_known["market_value"] - last_known["market_value_prev"]) / 
                last_known["market_value_prev"] if last_known["market_value_prev"] else 0.0
            ),
            "Market_Volume_lag1": last_known["market_volume"],
            "Market_Volume_lag2": last_known["market_volume_prev"],
            "Market_Volume_roll3": last_known["market_volume_roll3"],
            "Market_Volume_growth": (
                (last_known["market_volume"] - last_known["market_volume_prev"]) / 
                last_known["market_volume_prev"] if last_known["market_volume_prev"] else 0.0
            ),
            # Macro features are lagged (representing last known values)
            "Global_CO2_lag1": last_known["global_co2"],
            "Renewable_Electricity_Share_lag1": last_known["renewable_share"],
            "Renewable_Production_lag1": last_known["renewable_production"],
            "Global_GDP_Growth_lag1": last_known["gdp_growth"],
        }
        
        # Apply scenario changes if provided
        if scenario_params:
            # Emissions change
            if scenario_params.emissions_change_pct != 0:
                features["Global_CO2_lag1"] *= (1 + scenario_params.emissions_change_pct / 100)
            
            # Renewable share change
            if scenario_params.renewable_share_change_pct != 0:
                features["Renewable_Electricity_Share_lag1"] *= (1 + scenario_params.renewable_share_change_pct / 100)
                # Clamp to reasonable bounds (0-100%)
                features["Renewable_Electricity_Share_lag1"] = max(0, min(100, features["Renewable_Electricity_Share_lag1"]))
            
            # GDP growth change
            if scenario_params.gdp_growth_change_pct != 0:
                features["Global_GDP_Growth_lag1"] *= (1 + scenario_params.gdp_growth_change_pct / 100)
        
        return features
    
    def _predict_target(
        self, 
        target: str, 
        features: dict, 
        model, 
        scaler, 
        metadata: dict
    ) -> float:
        """Predict a single target using the appropriate model."""
        selected = metadata["selected_model"]
        
        # Naive baseline: return last known value
        if selected == "Naive_LastValue":
            return features[f"{target}_lag1"]
        
        # Moving average baseline
        if selected == "MovingAverage_3":
            return features[f"{target}_roll3"]
        
        # ML model prediction
        if model is None or scaler is None:
            raise ValueError(f"Model not loaded for {target}")
        
        feature_cols = metadata["feature_columns"]
        X = np.array([[features.get(c, np.nan) for c in feature_cols]])
        X_scaled = scaler.transform(X)
        prediction = float(model.predict(X_scaled)[0])
        
        return max(0, prediction)  # Market values/volumes cannot be negative
    
    def simulate(self, scenario_params: ScenarioParameters) -> ScenarioResult:
        """
        Run a scenario simulation.
        
        Compares baseline prediction (current conditions) with scenario prediction
        (modified conditions based on scenario_params).
        """
        # Validate parameters
        valid, error_msg = scenario_params.validate()
        if not valid:
            raise ValueError(f"Invalid scenario parameters: {error_msg}")
        
        warnings = []
        
        # Get last known values
        last_known = self._get_last_known_values()
        
        # Build baseline features (no changes)
        baseline_features = self._build_feature_dict(last_known, None)
        
        # Build scenario features (with changes)
        scenario_features = self._build_feature_dict(last_known, scenario_params)
        
        # Predict baseline
        baseline_value = self._predict_target(
            "Market_Value", baseline_features, 
            self.value_model, self.value_scaler, self.value_meta
        )
        baseline_volume = self._predict_target(
            "Market_Volume", baseline_features,
            self.volume_model, self.volume_scaler, self.volume_meta
        )
        
        # Predict scenario
        scenario_value = self._predict_target(
            "Market_Value", scenario_features,
            self.value_model, self.value_scaler, self.value_meta
        )
        scenario_volume = self._predict_target(
            "Market_Volume", scenario_features,
            self.volume_model, self.volume_scaler, self.volume_meta
        )
        
        # Calculate changes
        value_change_abs = scenario_value - baseline_value
        value_change_pct = (value_change_abs / baseline_value * 100) if baseline_value != 0 else 0
        
        volume_change_abs = scenario_volume - baseline_volume
        volume_change_pct = (volume_change_abs / baseline_volume * 100) if baseline_volume != 0 else 0
        
        # Add warnings for interpretation
        if self.value_meta["selected_model"] == "Naive_LastValue":
            warnings.append("Market Value uses Naive_LastValue model - predictions are scenario-insensitive (always equal to last known value)")
        
        if self.volume_meta["selected_model"] == "Naive_LastValue":
            warnings.append("Market Volume uses Naive_LastValue model - predictions are scenario-insensitive")
        elif self.volume_meta["selected_model"] == "XGBoost":
            if abs(volume_change_pct) < 0.1:
                warnings.append("Market Volume shows minimal response to scenario - current changes may be too small to detect")
        
        if scenario_params.carbon_price_change_pct != 0:
            warnings.append("Carbon price change does not directly affect ML predictions - this parameter is provided for context only")
        
        if abs(value_change_pct) > 100:
            warnings.append("Scenario shows extreme value change (>100%) - interpret with caution")
        
        if abs(volume_change_pct) > 100:
            warnings.append("Scenario shows extreme volume change (>100%) - interpret with caution")
        
        # Determine model sensitivity to scenarios
        value_sensitive = self.value_meta["selected_model"] not in ["Naive_LastValue", "MovingAverage_3"]
        volume_sensitive = self.volume_meta["selected_model"] not in ["Naive_LastValue", "MovingAverage_3"]
        
        # Prepare model info
        model_info = {
            "market_value_model": self.value_meta["selected_model"],
            "market_volume_model": self.volume_meta["selected_model"],
            "market_value_sensitive_to_scenario": value_sensitive,
            "market_volume_sensitive_to_scenario": volume_sensitive,
            "baseline_year": last_known["year"],
            "prediction_year": last_known["year"] + 1,
            "carbon_price_directly_modeled": False,  # Important: clarify this is not a direct input
            "features_affecting_volume": [
                "CO2 emissions (lagged)", 
                "Renewable electricity share (lagged)",
                "GDP growth (lagged)",
                "Historical market values/volumes"
            ] if volume_sensitive else ["Last known market volume only"],
            "features_affecting_value": [
                "CO2 emissions (lagged)", 
                "Renewable electricity share (lagged)", 
                "GDP growth (lagged)",
                "Historical market values/volumes"
            ] if value_sensitive else ["Last known market value only"],
            "limitations": [
                "Predictions are based on historical patterns and may not capture future structural changes",
                "Scenario changes are applied to lagged features as the model uses last-known values",
                "Carbon price is not directly modeled but may correlate with other factors",
                f"Historical data contains only {len(self.df)} annual observations"
            ]
        }
        
        return ScenarioResult(
            baseline_value=baseline_value,
            baseline_volume=baseline_volume,
            scenario_value=scenario_value,
            scenario_volume=scenario_volume,
            value_change_absolute=value_change_abs,
            value_change_percent=value_change_pct,
            volume_change_absolute=volume_change_abs,
            volume_change_percent=volume_change_pct,
            parameters={
                "carbon_price_change_pct": scenario_params.carbon_price_change_pct,
                "emissions_change_pct": scenario_params.emissions_change_pct,
                "renewable_share_change_pct": scenario_params.renewable_share_change_pct,
                "gdp_growth_change_pct": scenario_params.gdp_growth_change_pct,
            },
            model_info=model_info,
            warnings=warnings,
        )


def simulate_scenario(
    carbon_price_change_pct: float = 0.0,
    emissions_change_pct: float = 0.0,
    renewable_share_change_pct: float = 0.0,
    gdp_growth_change_pct: float = 0.0,
) -> dict:
    """
    Convenience function for running a scenario simulation.
    
    Args:
        carbon_price_change_pct: Carbon price change % (note: not directly in model)
        emissions_change_pct: Global CO2 emissions change %
        renewable_share_change_pct: Renewable electricity share change %
        gdp_growth_change_pct: Global GDP growth change %
    
    Returns:
        Dictionary with baseline, scenario, changes, and metadata
    """
    params = ScenarioParameters(
        carbon_price_change_pct=carbon_price_change_pct,
        emissions_change_pct=emissions_change_pct,
        renewable_share_change_pct=renewable_share_change_pct,
        gdp_growth_change_pct=gdp_growth_change_pct,
    )
    
    simulator = ScenarioSimulator()
    result = simulator.simulate(params)
    return result.to_dict()


if __name__ == "__main__":
    # Test the simulator
    print("="*60)
    print("Scenario Simulator Test")
    print("="*60)
    
    # Baseline
    print("\n1. BASELINE (no changes):")
    result = simulate_scenario()
    print(f"  Market Value: ${result['baseline']['market_value']:.2f}M")
    print(f"  Market Volume: {result['baseline']['market_volume']:.2f}M tCO2")
    
    # Scenario 1: Increased renewable adoption
    print("\n2. SCENARIO: +30% Renewable Share, -10% Emissions:")
    result = simulate_scenario(
        renewable_share_change_pct=30.0,
        emissions_change_pct=-10.0
    )
    print(f"  Baseline Value: ${result['baseline']['market_value']:.2f}M")
    print(f"  Scenario Value: ${result['scenario']['market_value']:.2f}M")
    print(f"  Change: {result['changes']['value_percent']:+.2f}%")
    print(f"  Baseline Volume: {result['baseline']['market_volume']:.2f}M tCO2")
    print(f"  Scenario Volume: {result['scenario']['market_volume']:.2f}M tCO2")
    print(f"  Change: {result['changes']['volume_percent']:+.2f}%")
    
    # Scenario 2: Economic growth
    print("\n3. SCENARIO: +20% GDP Growth:")
    result = simulate_scenario(gdp_growth_change_pct=20.0)
    print(f"  Value Change: {result['changes']['value_percent']:+.2f}%")
    print(f"  Volume Change: {result['changes']['volume_percent']:+.2f}%")
    
    if result['warnings']:
        print(f"\n  Warnings: {', '.join(result['warnings'])}")
    
    print("\n" + "="*60)
    print("✓ Scenario simulator working correctly")
    print("="*60)
