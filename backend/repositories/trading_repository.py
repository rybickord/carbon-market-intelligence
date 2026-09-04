"""
Repository for trading data access.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database.models import CompanyTrading, PredictionRequest


class TradingRepository:
    """Repository for accessing company trading data and prediction history."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_transactions(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyTrading]:
        """Get company trading transactions with pagination."""
        return self.db.query(CompanyTrading).order_by(
            desc(CompanyTrading.date)
        ).offset(skip).limit(limit).all()
    
    def get_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyTrading]:
        """Get transactions for a specific company."""
        return self.db.query(CompanyTrading).filter(
            CompanyTrading.company_id == company_id
        ).order_by(
            desc(CompanyTrading.date)
        ).offset(skip).limit(limit).all()
    
    def get_by_industry(
        self,
        industry_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyTrading]:
        """Get transactions for a specific industry."""
        return self.db.query(CompanyTrading).filter(
            CompanyTrading.industry_type == industry_type
        ).order_by(
            desc(CompanyTrading.date)
        ).offset(skip).limit(limit).all()
    
    def save_prediction(
        self,
        industry_type: str,
        fuel_type: str,
        verification_status: str,
        energy_demand_mwh: float,
        emission_produced_tco2: float,
        emission_allowance_tco2: float,
        carbon_price_usd_per_t: float,
        compliance_cost_usd: float,
        predicted_action: str,
        probability: float,
        confidence: str,
        model_used: str
    ) -> PredictionRequest:
        """Save a prediction request to the database."""
        prediction = PredictionRequest(
            industry_type=industry_type,
            fuel_type=fuel_type,
            verification_status=verification_status,
            energy_demand_mwh=energy_demand_mwh,
            emission_produced_tco2=emission_produced_tco2,
            emission_allowance_tco2=emission_allowance_tco2,
            carbon_price_usd_per_t=carbon_price_usd_per_t,
            compliance_cost_usd=compliance_cost_usd,
            predicted_action=predicted_action,
            probability=probability,
            confidence=confidence,
            model_used=model_used
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction
    
    def get_recent_predictions(
        self,
        limit: int = 100
    ) -> List[PredictionRequest]:
        """Get recent prediction requests."""
        return self.db.query(PredictionRequest).order_by(
            desc(PredictionRequest.created_at)
        ).limit(limit).all()
    
    def get_prediction_stats(self) -> dict:
        """Get statistics about prediction history."""
        total = self.db.query(PredictionRequest).count()
        buy_count = self.db.query(PredictionRequest).filter(
            PredictionRequest.predicted_action == 'Buy'
        ).count()
        sell_count = self.db.query(PredictionRequest).filter(
            PredictionRequest.predicted_action == 'Sell'
        ).count()
        
        return {
            'total_predictions': total,
            'buy_predictions': buy_count,
            'sell_predictions': sell_count
        }
