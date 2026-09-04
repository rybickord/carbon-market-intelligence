"""
Repository for market data access.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database.models import MarketData, ForecastResult


class MarketRepository:
    """Repository for accessing market data from database."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_timeseries(self) -> List[MarketData]:
        """Get all historical market data ordered by year."""
        return self.db.query(MarketData).order_by(MarketData.year).all()
    
    def get_latest(self) -> Optional[MarketData]:
        """Get the most recent market data point."""
        return self.db.query(MarketData).order_by(desc(MarketData.year)).first()
    
    def get_by_year(self, year: int) -> Optional[MarketData]:
        """Get market data for a specific year."""
        return self.db.query(MarketData).filter(MarketData.year == year).first()
    
    def get_forecast(self) -> List[ForecastResult]:
        """Get forecast results (historical + predictions) ordered by year."""
        return self.db.query(ForecastResult).order_by(ForecastResult.year).all()
    
    def get_forecast_by_series(self, series: str) -> List[ForecastResult]:
        """Get forecast results filtered by series type ('historical' or 'forecast')."""
        return self.db.query(ForecastResult).filter(
            ForecastResult.series == series
        ).order_by(ForecastResult.year).all()
