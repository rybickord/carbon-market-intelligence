"""
Repository for scenario simulation results.
"""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database.models import ScenarioResult


class ScenarioRepository:
    """Repository for accessing scenario simulation history."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_scenario(
        self,
        carbon_price_change_pct: float,
        emissions_change_pct: float,
        renewable_share_change_pct: float,
        gdp_growth_change_pct: float,
        baseline_market_value: float,
        baseline_market_volume: float,
        scenario_market_value: float,
        scenario_market_volume: float,
        value_change: float,
        value_change_pct: float,
        volume_change: float,
        volume_change_pct: float,
        model_info: dict,
        warnings: list
    ) -> ScenarioResult:
        """Save a scenario simulation result to the database."""
        scenario = ScenarioResult(
            carbon_price_change_pct=carbon_price_change_pct,
            emissions_change_pct=emissions_change_pct,
            renewable_share_change_pct=renewable_share_change_pct,
            gdp_growth_change_pct=gdp_growth_change_pct,
            baseline_market_value=baseline_market_value,
            baseline_market_volume=baseline_market_volume,
            scenario_market_value=scenario_market_value,
            scenario_market_volume=scenario_market_volume,
            value_change=value_change,
            value_change_pct=value_change_pct,
            volume_change=volume_change,
            volume_change_pct=volume_change_pct,
            model_info=json.dumps(model_info),
            warnings=json.dumps(warnings)
        )
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario
    
    def get_recent_scenarios(
        self,
        limit: int = 100
    ) -> List[ScenarioResult]:
        """Get recent scenario simulations."""
        return self.db.query(ScenarioResult).order_by(
            desc(ScenarioResult.created_at)
        ).limit(limit).all()
    
    def get_scenario_by_id(self, scenario_id: int) -> Optional[ScenarioResult]:
        """Get a specific scenario by ID."""
        return self.db.query(ScenarioResult).filter(
            ScenarioResult.id == scenario_id
        ).first()
    
    def get_scenario_stats(self) -> dict:
        """Get statistics about scenario simulations."""
        total = self.db.query(ScenarioResult).count()
        
        return {
            'total_scenarios': total
        }
