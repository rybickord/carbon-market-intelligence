"""
SQLAlchemy database models.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from backend.database.database import Base


class MarketData(Base):
    """Global carbon market historical data."""
    
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, unique=True, index=True)
    market_value = Column(Float, nullable=False)
    market_volume = Column(Float, nullable=False)
    global_co2 = Column(Float)
    renewable_electricity_share = Column(Float)
    renewable_production = Column(Float)
    global_gdp_growth = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MarketData(year={self.year}, value={self.market_value}, volume={self.market_volume})>"


class CountryIntelligence(Base):
    """Country-level intelligence data by year."""
    
    __tablename__ = "country_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), nullable=False, index=True)
    iso = Column(String(10), index=True)
    year = Column(Integer, nullable=False, index=True)
    co2 = Column(Float)
    per_capita_co2 = Column(Float)
    renewable_electricity_share = Column(Float)
    renewable_production = Column(Float)
    gdp_growth = Column(Float)
    carbon_rate_2023 = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('country', 'year', name='uq_country_year'),
        Index('ix_country_intelligence_country_year', 'country', 'year'),
    )
    
    def __repr__(self):
        return f"<CountryIntelligence(country={self.country}, year={self.year})>"


class CompanyTrading(Base):
    """Company trading transactions dataset."""
    
    __tablename__ = "company_trading"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(20), nullable=False, index=True)
    industry_type = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    energy_demand_mwh = Column(Float, nullable=False)
    fuel_type = Column(String(50), nullable=False)
    emission_produced_tco2 = Column(Float, nullable=False)
    emission_allowance_tco2 = Column(Float, nullable=False)
    carbon_price_usd_per_t = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    credits_traded_tco2 = Column(Float, nullable=False)
    verification_status = Column(String(20), nullable=False)
    compliance_cost_usd = Column(Float, nullable=False)
    optimization_scenario = Column(String(50))
    carbon_cost_savings_usd = Column(Float)
    target_trade_action = Column(Integer)  # 0=Sell, 1=Buy
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('ix_company_trading_company_date', 'company_id', 'date'),
        Index('ix_company_trading_industry', 'industry_type'),
    )
    
    def __repr__(self):
        return f"<CompanyTrading(company={self.company_id}, date={self.date})>"


class CountryScore(Base):
    """Country risk and opportunity scores."""
    
    __tablename__ = "country_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), nullable=False, index=True)
    iso = Column(String(10))
    year = Column(Integer, nullable=False)
    
    # Risk components
    risk_score = Column(Float)
    risk_category = Column(String(20))
    comp_co2 = Column(Float)
    comp_per_cap = Column(Float)
    comp_renew_weak = Column(Float)
    comp_gdp_weak = Column(Float)
    comp_policy_weak = Column(Float)
    
    # Opportunity components
    opportunity_score = Column(Float)
    opportunity_category = Column(String(20))
    comp_renew_elec = Column(Float)
    comp_renew_prod = Column(Float)
    comp_transition = Column(Float)
    comp_econ_res = Column(Float)
    comp_policy_enable = Column(Float)
    
    # Flags for imputed values
    flag_renewable_imputed = Column(String(10))
    flag_gdp_imputed = Column(String(10))
    flag_carbon_rate_imputed = Column(String(10))
    flag_renew_elec_imputed = Column(String(10))
    flag_renew_prod_imputed = Column(String(10))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('country', 'year', name='uq_country_score_year'),
        Index('ix_country_scores_country_year', 'country', 'year'),
        Index('ix_country_scores_risk', 'risk_score'),
        Index('ix_country_scores_opportunity', 'opportunity_score'),
    )
    
    def __repr__(self):
        return f"<CountryScore(country={self.country}, risk={self.risk_score}, opp={self.opportunity_score})>"


class ForecastResult(Base):
    """Global market forecast results."""
    
    __tablename__ = "forecast_results"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, unique=True, index=True)
    market_value = Column(Float, nullable=False)
    market_volume = Column(Float, nullable=False)
    series = Column(String(20), nullable=False)  # 'historical' or 'forecast'
    market_value_model = Column(String(50))
    market_volume_model = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ForecastResult(year={self.year}, series={self.series})>"


class ScenarioResult(Base):
    """Scenario simulation history."""
    
    __tablename__ = "scenario_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Scenario parameters
    carbon_price_change_pct = Column(Float, nullable=False)
    emissions_change_pct = Column(Float, nullable=False)
    renewable_share_change_pct = Column(Float, nullable=False)
    gdp_growth_change_pct = Column(Float, nullable=False)
    
    # Baseline results
    baseline_market_value = Column(Float, nullable=False)
    baseline_market_volume = Column(Float, nullable=False)
    
    # Scenario results
    scenario_market_value = Column(Float, nullable=False)
    scenario_market_volume = Column(Float, nullable=False)
    
    # Changes
    value_change = Column(Float, nullable=False)
    value_change_pct = Column(Float, nullable=False)
    volume_change = Column(Float, nullable=False)
    volume_change_pct = Column(Float, nullable=False)
    
    # Metadata
    model_info = Column(Text)  # JSON string
    warnings = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<ScenarioResult(id={self.id}, created={self.created_at})>"


class PredictionRequest(Base):
    """Company trading prediction request history."""
    
    __tablename__ = "prediction_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Input features
    industry_type = Column(String(50), nullable=False)
    fuel_type = Column(String(50), nullable=False)
    verification_status = Column(String(20), nullable=False)
    energy_demand_mwh = Column(Float, nullable=False)
    emission_produced_tco2 = Column(Float, nullable=False)
    emission_allowance_tco2 = Column(Float, nullable=False)
    carbon_price_usd_per_t = Column(Float, nullable=False)
    compliance_cost_usd = Column(Float, nullable=False)
    
    # Prediction output
    predicted_action = Column(String(10), nullable=False)  # 'Buy' or 'Sell'
    probability = Column(Float, nullable=False)
    confidence = Column(String(20), nullable=False)  # 'Low', 'Medium', 'High'
    model_used = Column(String(50), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<PredictionRequest(id={self.id}, action={self.predicted_action})>"
