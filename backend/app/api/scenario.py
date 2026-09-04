"""
Scenario simulation endpoint.
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException

from backend.app.schemas import ScenarioRequest, ScenarioResponse

router = APIRouter()

# Add ml module to path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.scenario_simulator import ScenarioSimulator, ScenarioParameters

# Initialize simulator on startup
_simulator = None


def get_simulator():
    """Get or create scenario simulator instance."""
    global _simulator
    if _simulator is None:
        _simulator = ScenarioSimulator()
        print("✓ Scenario simulator initialized")
    return _simulator


@router.post("/simulate", response_model=ScenarioResponse)
async def simulate_scenario(request: ScenarioRequest):
    """
    Run a scenario simulation to compare baseline vs scenario predictions.
    
    Modifies key market conditions and predicts impact on market value and volume.
    """
    try:
        simulator = get_simulator()
        
        # Create scenario parameters
        params = ScenarioParameters(
            carbon_price_change_pct=request.carbon_price_change_pct,
            emissions_change_pct=request.emissions_change_pct,
            renewable_share_change_pct=request.renewable_share_change_pct,
            gdp_growth_change_pct=request.gdp_growth_change_pct
        )
        
        # Run simulation
        result = simulator.simulate(params)
        
        # Convert to dict for response
        return ScenarioResponse(**result.to_dict())
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid scenario parameters: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
