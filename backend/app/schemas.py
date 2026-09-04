"""
Pydantic schemas for request/response validation.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# Market schemas
class MarketOverview(BaseModel):
    """Global market overview response."""
    latest_year: int
    latest_value: float
    latest_volume: float
    previous_value: Optional[float]
    previous_volume: Optional[float]
    value_growth_pct: Optional[float]
    volume_growth_pct: Optional[float]
    forecast_available: bool


class MarketHistoryPoint(BaseModel):
    """Single point in market history."""
    year: int
    market_value: float
    market_volume: float


class MarketForecastPoint(BaseModel):
    """Single point in market forecast."""
    year: int
    market_value: float
    market_volume: float
    series: str  # 'historical' or 'forecast'
    value_model: Optional[str] = None
    volume_model: Optional[str] = None


# Country schemas
class CountryListItem(BaseModel):
    """Country in list view."""
    country: str
    iso: Optional[str]
    latest_year: int
    co2: Optional[float]
    per_capita_co2: Optional[float]
    renewable_share: Optional[float]
    risk_score: Optional[float]
    opportunity_score: Optional[float]


class CountryDetail(BaseModel):
    """Detailed country information."""
    country: str
    iso: Optional[str]
    year: int
    co2: Optional[float]
    per_capita_co2: Optional[float]
    renewable_share: Optional[float]
    renewable_production: Optional[float]
    gdp_growth: Optional[float]
    carbon_rate_2023: Optional[float]
    risk_score: Optional[float]
    risk_category: Optional[str]
    opportunity_score: Optional[float]
    opportunity_category: Optional[str]


class CountryRiskItem(BaseModel):
    """Country risk ranking item."""
    rank: int
    country: str
    iso: Optional[str]
    risk_score: float
    risk_category: str
    co2: Optional[float]
    per_capita_co2: Optional[float]


class CountryOpportunityItem(BaseModel):
    """Country opportunity ranking item."""
    rank: int
    country: str
    iso: Optional[str]
    opportunity_score: float
    opportunity_category: str
    renewable_share: Optional[float]
    gdp_growth: Optional[float]


# Trading schemas
class TradingModelInfo(BaseModel):
    """Trading model metadata."""
    model_name: str
    target: str
    target_interpretation: str
    validation: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    input_features: List[str]


class TradingPredictionRequest(BaseModel):
    """Request for trading prediction."""
    industry_type: str = Field(..., description="Industry type: Cement, Energy, Manufacturing, Steel")
    fuel_type: str = Field(..., description="Fuel type: Coal, Mixed Fuel, Natural Gas, Renewable")
    verification_status: str = Field(..., description="Verification status: Disputed, Verified")
    energy_demand_mwh: float = Field(..., gt=0, description="Energy demand in MWh")
    emission_produced_tco2: float = Field(..., gt=0, description="Emissions produced in tCO2")
    emission_allowance_tco2: float = Field(..., gt=0, description="Emission allowance in tCO2")
    carbon_price_usd_per_t: float = Field(..., gt=0, description="Carbon price in USD per ton")
    compliance_cost_usd: float = Field(..., ge=0, description="Compliance cost in USD")
    
    @field_validator('industry_type')
    @classmethod
    def validate_industry(cls, v):
        valid = ['Cement', 'Energy', 'Manufacturing', 'Steel']
        if v not in valid:
            raise ValueError(f"industry_type must be one of {valid}")
        return v
    
    @field_validator('fuel_type')
    @classmethod
    def validate_fuel(cls, v):
        valid = ['Coal', 'Mixed Fuel', 'Natural Gas', 'Renewable']
        if v not in valid:
            raise ValueError(f"fuel_type must be one of {valid}")
        return v
    
    @field_validator('verification_status')
    @classmethod
    def validate_verification(cls, v):
        valid = ['Disputed', 'Verified']
        if v not in valid:
            raise ValueError(f"verification_status must be one of {valid}")
        return v


class TradingPredictionResponse(BaseModel):
    """Response for trading prediction."""
    predicted_action: str  # 'Buy' or 'Sell'
    probability: float
    confidence: str  # 'Low', 'Medium', 'High'
    model_used: str
    input_summary: dict


# Scenario schemas
class ScenarioRequest(BaseModel):
    """Request for scenario simulation."""
    carbon_price_change_pct: float = Field(0.0, ge=-50, le=200, description="Carbon price change %")
    emissions_change_pct: float = Field(0.0, ge=-30, le=50, description="Emissions change %")
    renewable_share_change_pct: float = Field(0.0, ge=-20, le=100, description="Renewable share change %")
    gdp_growth_change_pct: float = Field(0.0, ge=-20, le=50, description="GDP growth change %")


class ScenarioResponse(BaseModel):
    """Response for scenario simulation."""
    baseline: dict
    scenario: dict
    changes: dict
    scenario_parameters: dict
    model_info: dict
    warnings: List[str]
