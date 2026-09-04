"""
Data service for loading and caching processed datasets.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

import pandas as pd

# Project root
ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"


class DataService:
    """Service for accessing processed data with caching."""
    
    _instance = None
    _data_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._load_all_data()
    
    def _load_all_data(self):
        """Load all processed datasets into memory on startup."""
        print("Loading processed datasets...")
        
        # Market data
        self._data_cache['global_market_timeseries'] = pd.read_csv(
            PROCESSED_DIR / "global_market_timeseries.csv"
        )
        self._data_cache['global_market_forecast'] = pd.read_csv(
            PROCESSED_DIR / "global_market_forecast.csv"
        )
        self._data_cache['global_market_walkforward'] = pd.read_csv(
            PROCESSED_DIR / "global_market_walkforward.csv"
        )
        
        # Country data
        self._data_cache['country_intelligence'] = pd.read_csv(
            PROCESSED_DIR / "country_intelligence.csv"
        )
        self._data_cache['country_risk_scores'] = pd.read_csv(
            PROCESSED_DIR / "country_risk_scores.csv"
        )
        self._data_cache['country_opportunity_scores'] = pd.read_csv(
            PROCESSED_DIR / "country_opportunity_scores.csv"
        )
        
        # Company trading data
        self._data_cache['company_trading_dataset'] = pd.read_csv(
            PROCESSED_DIR / "company_trading_dataset.csv"
        )
        
        # JSON metadata
        with open(PROCESSED_DIR / "global_market_model_metrics.json") as f:
            self._data_cache['global_market_model_metrics'] = json.load(f)
        
        with open(PROCESSED_DIR / "company_trading_evaluation.json") as f:
            self._data_cache['company_trading_evaluation'] = json.load(f)
        
        print(f"✓ Loaded {len(self._data_cache)} datasets")
    
    def get_global_market_timeseries(self) -> pd.DataFrame:
        """Get historical market timeseries data."""
        return self._data_cache['global_market_timeseries'].copy()
    
    def get_global_market_forecast(self) -> pd.DataFrame:
        """Get market forecast data (historical + future predictions)."""
        return self._data_cache['global_market_forecast'].copy()
    
    def get_global_market_walkforward(self) -> pd.DataFrame:
        """Get walk-forward validation results."""
        return self._data_cache['global_market_walkforward'].copy()
    
    def get_global_market_metrics(self) -> dict:
        """Get model evaluation metrics."""
        return self._data_cache['global_market_model_metrics'].copy()
    
    def get_country_intelligence(self, country: Optional[str] = None) -> pd.DataFrame:
        """
        Get country intelligence data.
        
        Args:
            country: Optional country name to filter by
        """
        df = self._data_cache['country_intelligence'].copy()
        if country:
            df = df[df['Country'].str.lower() == country.lower()]
        return df
    
    def get_country_risk_scores(self) -> pd.DataFrame:
        """Get country risk scores (latest year only)."""
        return self._data_cache['country_risk_scores'].copy()
    
    def get_country_opportunity_scores(self) -> pd.DataFrame:
        """Get country opportunity scores (latest year only)."""
        return self._data_cache['country_opportunity_scores'].copy()
    
    def get_company_trading_dataset(self) -> pd.DataFrame:
        """Get company trading dataset."""
        return self._data_cache['company_trading_dataset'].copy()
    
    def get_company_trading_evaluation(self) -> dict:
        """Get company trading model evaluation metrics."""
        return self._data_cache['company_trading_evaluation'].copy()
    
    def get_unique_countries(self) -> list[str]:
        """Get list of unique countries from intelligence data."""
        df = self._data_cache['country_intelligence']
        return sorted(df['Country'].unique().tolist())
    
    def country_exists(self, country: str) -> bool:
        """Check if a country exists in the dataset."""
        countries = self.get_unique_countries()
        return country in countries or country.lower() in [c.lower() for c in countries]
    
    def get_country_detail(self, country: str) -> Optional[dict]:
        """
        Get detailed information for a specific country.
        
        Returns the latest year data with risk and opportunity scores.
        """
        # Get latest intelligence data
        intel = self.get_country_intelligence(country)
        if intel.empty:
            return None
        
        # Get latest year
        latest = intel.sort_values('Year', ascending=False).iloc[0]
        
        # Get risk score
        risk_df = self._data_cache['country_risk_scores']
        risk_row = risk_df[risk_df['Country'].str.lower() == country.lower()]
        
        # Get opportunity score
        opp_df = self._data_cache['country_opportunity_scores']
        opp_row = opp_df[opp_df['Country'].str.lower() == country.lower()]
        
        result = {
            "country": latest['Country'],
            "iso": latest['ISO'] if pd.notna(latest['ISO']) else None,
            "year": int(latest['Year']),
            "co2": float(latest['CO2']) if pd.notna(latest['CO2']) else None,
            "per_capita_co2": float(latest['Per_Capita_CO2']) if pd.notna(latest['Per_Capita_CO2']) else None,
            "renewable_share": float(latest['Renewable_Electricity_Share']) if pd.notna(latest['Renewable_Electricity_Share']) else None,
            "renewable_production": float(latest['Renewable_Production']) if pd.notna(latest['Renewable_Production']) else None,
            "gdp_growth": float(latest['GDP_Growth']) if pd.notna(latest['GDP_Growth']) else None,
            "carbon_rate_2023": float(latest['Carbon_Rate_2023']) if pd.notna(latest['Carbon_Rate_2023']) else None,
        }
        
        # Add risk score if available
        if not risk_row.empty:
            risk = risk_row.iloc[0]
            result['risk_score'] = float(risk['Risk_Score'])
            result['risk_category'] = risk['Risk_Category']
        else:
            result['risk_score'] = None
            result['risk_category'] = None
        
        # Add opportunity score if available
        if not opp_row.empty:
            opp = opp_row.iloc[0]
            result['opportunity_score'] = float(opp['Opportunity_Score'])
            result['opportunity_category'] = opp['Opportunity_Category']
        else:
            result['opportunity_score'] = None
            result['opportunity_category'] = None
        
        return result


# Singleton instance
_data_service = DataService()


def get_data_service() -> DataService:
    """Get the singleton DataService instance."""
    return _data_service
