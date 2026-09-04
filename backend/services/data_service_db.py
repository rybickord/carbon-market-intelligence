"""
Database-backed data service for loading and accessing data from PostgreSQL.
Falls back to CSV if database is unavailable.
"""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, List, Dict

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

# Project root
ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"


class DataServiceDB:
    """
    Database-backed data service with CSV fallback.
    
    Attempts to use PostgreSQL if available, falls back to CSV files.
    """
    
    _instance = None
    _use_database = False
    _db_available = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._check_database_availability()
            if not self._use_database:
                self._load_csv_fallback()
    
    def _check_database_availability(self):
        """Check if database is available and accessible."""
        try:
            from backend.database.database import SessionLocal
            db = SessionLocal()
            # Test connection with a simple query
            db.execute("SELECT 1")
            db.close()
            self._use_database = True
            self._db_available = True
            print("✓ Using PostgreSQL database for data access")
        except (ImportError, OperationalError, Exception) as e:
            self._use_database = False
            self._db_available = False
            print(f"⚠ Database not available ({str(e)}), falling back to CSV files")
    
    def _load_csv_fallback(self):
        """Load CSV files as fallback when database is unavailable."""
        from backend.services.data_service import DataService
        self._csv_service = DataService()
        print("✓ Using CSV files for data access")
    
    def _get_db(self) -> Session:
        """Get database session."""
        from backend.database.database import SessionLocal
        return SessionLocal()
    
    def get_global_market_timeseries(self) -> pd.DataFrame:
        """Get historical market timeseries data."""
        if self._use_database:
            from backend.repositories.market_repository import MarketRepository
            db = self._get_db()
            try:
                repo = MarketRepository(db)
                records = repo.get_timeseries()
                
                # Convert to DataFrame
                data = [{
                    'Year': r.year,
                    'Market_Value': r.market_value,
                    'Market_Volume': r.market_volume,
                    'Global_CO2': r.global_co2,
                    'Renewable_Electricity_Share': r.renewable_electricity_share,
                    'Renewable_Production': r.renewable_production,
                    'Global_GDP_Growth': r.global_gdp_growth,
                } for r in records]
                
                return pd.DataFrame(data)
            finally:
                db.close()
        else:
            return self._csv_service.get_global_market_timeseries()
    
    def get_global_market_forecast(self) -> pd.DataFrame:
        """Get market forecast data (historical + future predictions)."""
        if self._use_database:
            from backend.repositories.market_repository import MarketRepository
            db = self._get_db()
            try:
                repo = MarketRepository(db)
                records = repo.get_forecast()
                
                # Convert to DataFrame
                data = [{
                    'Year': r.year,
                    'Market_Value': r.market_value,
                    'Market_Volume': r.market_volume,
                    'Series': r.series,
                    'Market_Value_model': r.market_value_model,
                    'Market_Volume_model': r.market_volume_model,
                } for r in records]
                
                return pd.DataFrame(data)
            finally:
                db.close()
        else:
            return self._csv_service.get_global_market_forecast()
    
    def get_global_market_walkforward(self) -> pd.DataFrame:
        """Get walk-forward validation results."""
        # This is always from CSV as it's not stored in database
        if self._use_database:
            return pd.read_csv(PROCESSED_DIR / "global_market_walkforward.csv")
        else:
            return self._csv_service.get_global_market_walkforward()
    
    def get_global_market_metrics(self) -> dict:
        """Get model evaluation metrics."""
        # This is always from JSON as it's not stored in database
        if self._use_database:
            with open(PROCESSED_DIR / "global_market_model_metrics.json") as f:
                return json.load(f)
        else:
            return self._csv_service.get_global_market_metrics()
    
    def get_country_intelligence(self, country: Optional[str] = None) -> pd.DataFrame:
        """
        Get country intelligence data.
        
        Args:
            country: Optional country name to filter by
        """
        if self._use_database:
            from backend.repositories.country_repository import CountryRepository
            db = self._get_db()
            try:
                repo = CountryRepository(db)
                records = repo.get_country_intelligence(country=country)
                
                # Convert to DataFrame
                data = [{
                    'Country': r.country,
                    'ISO': r.iso,
                    'Year': r.year,
                    'CO2': r.co2,
                    'Per_Capita_CO2': r.per_capita_co2,
                    'Renewable_Electricity_Share': r.renewable_electricity_share,
                    'Renewable_Production': r.renewable_production,
                    'GDP_Growth': r.gdp_growth,
                    'Carbon_Rate_2023': r.carbon_rate_2023,
                } for r in records]
                
                return pd.DataFrame(data)
            finally:
                db.close()
        else:
            return self._csv_service.get_country_intelligence(country=country)
    
    def get_country_risk_scores(self) -> pd.DataFrame:
        """Get country risk scores (latest year only)."""
        if self._use_database:
            from backend.repositories.country_repository import CountryRepository
            db = self._get_db()
            try:
                repo = CountryRepository(db)
                records = repo.get_risk_ranking()
                
                # Convert to DataFrame
                data = [{
                    'Country': r.country,
                    'ISO': r.iso,
                    'Year': r.year,
                    'Risk_Score': r.risk_score,
                    'Risk_Category': r.risk_category,
                    'CO2': None,  # Not stored in CountryScore, would need join
                    'Per_Capita_CO2': None,
                } for r in records]
                
                return pd.DataFrame(data)
            finally:
                db.close()
        else:
            return self._csv_service.get_country_risk_scores()
    
    def get_country_opportunity_scores(self) -> pd.DataFrame:
        """Get country opportunity scores (latest year only)."""
        if self._use_database:
            from backend.repositories.country_repository import CountryRepository
            db = self._get_db()
            try:
                repo = CountryRepository(db)
                records = repo.get_opportunity_ranking()
                
                # Convert to DataFrame
                data = [{
                    'Country': r.country,
                    'ISO': r.iso,
                    'Year': r.year,
                    'Opportunity_Score': r.opportunity_score,
                    'Opportunity_Category': r.opportunity_category,
                    'Renewable_Electricity_Share': None,  # Would need join
                    'GDP_Growth': None,
                } for r in records]
                
                return pd.DataFrame(data)
            finally:
                db.close()
        else:
            return self._csv_service.get_country_opportunity_scores()
    
    def get_company_trading_dataset(self) -> pd.DataFrame:
        """Get company trading dataset."""
        if self._use_database:
            from backend.repositories.trading_repository import TradingRepository
            db = self._get_db()
            try:
                repo = TradingRepository(db)
                # Get a sample for prediction (limit to avoid loading entire dataset)
                records = repo.get_all_transactions(limit=5000)
                
                # Convert to DataFrame
                data = [{
                    'Company_ID': r.company_id,
                    'Industry_Type': r.industry_type,
                    'Date': r.date,
                    'Energy_Demand_MWh': r.energy_demand_mwh,
                    'Fuel_Type': r.fuel_type,
                    'Emission_Produced_tCO2': r.emission_produced_tco2,
                    'Emission_Allowance_tCO2': r.emission_allowance_tco2,
                    'Carbon_Price_USD_per_t': r.carbon_price_usd_per_t,
                    'Transaction_Type': r.transaction_type,
                    'Credits_Traded_tCO2': r.credits_traded_tco2,
                    'Verification_Status': r.verification_status,
                    'Compliance_Cost_USD': r.compliance_cost_usd,
                    'Optimization_Scenario': r.optimization_scenario,
                    'Carbon_Cost_Savings_USD': r.carbon_cost_savings_usd,
                    'Target_Trade_Action': r.target_trade_action,
                } for r in records]
                
                return pd.DataFrame(data)
            finally:
                db.close()
        else:
            return self._csv_service.get_company_trading_dataset()
    
    def get_company_trading_evaluation(self) -> dict:
        """Get company trading model evaluation metrics."""
        # This is always from JSON as it's not stored in database
        if self._use_database:
            with open(PROCESSED_DIR / "company_trading_evaluation.json") as f:
                return json.load(f)
        else:
            return self._csv_service.get_company_trading_evaluation()
    
    def get_unique_countries(self) -> list[str]:
        """Get list of unique countries from intelligence data."""
        if self._use_database:
            from backend.repositories.country_repository import CountryRepository
            db = self._get_db()
            try:
                repo = CountryRepository(db)
                return repo.get_all_countries()
            finally:
                db.close()
        else:
            return self._csv_service.get_unique_countries()
    
    def country_exists(self, country: str) -> bool:
        """Check if a country exists in the dataset."""
        if self._use_database:
            from backend.repositories.country_repository import CountryRepository
            db = self._get_db()
            try:
                repo = CountryRepository(db)
                return repo.country_exists(country)
            finally:
                db.close()
        else:
            return self._csv_service.country_exists(country)
    
    def get_country_detail(self, country: str) -> Optional[dict]:
        """
        Get detailed information for a specific country.
        
        Returns the latest year data with risk and opportunity scores.
        """
        if self._use_database:
            from backend.repositories.country_repository import CountryRepository
            db = self._get_db()
            try:
                repo = CountryRepository(db)
                
                # Get latest intelligence
                intel = repo.get_country_latest(country)
                if not intel:
                    return None
                
                # Get scores
                scores = repo.get_country_score(country)
                
                result = {
                    "country": intel.country,
                    "iso": intel.iso,
                    "year": intel.year,
                    "co2": intel.co2,
                    "per_capita_co2": intel.per_capita_co2,
                    "renewable_share": intel.renewable_electricity_share,
                    "renewable_production": intel.renewable_production,
                    "gdp_growth": intel.gdp_growth,
                    "carbon_rate_2023": intel.carbon_rate_2023,
                }
                
                if scores:
                    result['risk_score'] = scores.risk_score
                    result['risk_category'] = scores.risk_category
                    result['opportunity_score'] = scores.opportunity_score
                    result['opportunity_category'] = scores.opportunity_category
                else:
                    result['risk_score'] = None
                    result['risk_category'] = None
                    result['opportunity_score'] = None
                    result['opportunity_category'] = None
                
                return result
            finally:
                db.close()
        else:
            return self._csv_service.get_country_detail(country)
    
    def is_database_available(self) -> bool:
        """Check if database is available."""
        return self._db_available
    
    def get_data_source(self) -> str:
        """Get current data source (database or csv)."""
        return "database" if self._use_database else "csv"


# Singleton instance
_data_service_db = DataServiceDB()


def get_data_service_db() -> DataServiceDB:
    """Get the singleton DataServiceDB instance."""
    return _data_service_db
