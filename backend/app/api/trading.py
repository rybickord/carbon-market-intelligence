"""
Trading endpoints for company carbon trading prediction.
"""

import json
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
import joblib
import numpy as np
import pandas as pd

from backend.app.schemas import TradingModelInfo, TradingPredictionRequest, TradingPredictionResponse
from backend.services.data_service import get_data_service

router = APIRouter()
data_service = get_data_service()

# Load trading model on startup
ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT / "ml" / "models" / "company_trading"

_trading_model = None
_trading_preprocessor = None
_trading_metadata = None


def load_trading_model():
    """Load trading model artifacts."""
    global _trading_model, _trading_preprocessor, _trading_metadata
    
    if _trading_model is None:
        _trading_model = joblib.load(MODELS_DIR / "classifier.pkl")
        _trading_preprocessor = joblib.load(MODELS_DIR / "preprocessor.pkl")
        
        with open(MODELS_DIR / "metadata.json") as f:
            _trading_metadata = json.load(f)
        
        print("✓ Trading model loaded")


# Load model on module import
load_trading_model()


@router.get("/model", response_model=TradingModelInfo)
async def get_trading_model_info():
    """
    Get trading model metadata and performance metrics.
    """
    try:
        eval_data = data_service.get_company_trading_evaluation()
        
        return TradingModelInfo(
            model_name=_trading_metadata['selected_model'],
            target=_trading_metadata['target'],
            target_interpretation=_trading_metadata['target_interpretation'],
            validation=_trading_metadata['validation'],
            accuracy=eval_data['metrics']['Accuracy'],
            precision=eval_data['metrics']['Precision'],
            recall=eval_data['metrics']['Recall'],
            f1_score=eval_data['metrics']['F1'],
            roc_auc=eval_data['metrics']['ROC_AUC'],
            input_features=_trading_metadata['input_fields']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model info: {str(e)}")


@router.post("/predict", response_model=TradingPredictionResponse)
async def predict_trade_action(request: TradingPredictionRequest):
    """
    Predict whether a company should Buy or Sell carbon credits.
    
    Uses only pre-decision features (no leakage).
    """
    try:
        # Build input dataframe with exact column names expected by preprocessor
        input_data = pd.DataFrame([{
            'Industry_Type': request.industry_type,
            'Fuel_Type': request.fuel_type,
            'Verification_Status': request.verification_status,
            'Energy_Demand_MWh': request.energy_demand_mwh,
            'Emission_Produced_tCO2': request.emission_produced_tco2,
            'Emission_Allowance_tCO2': request.emission_allowance_tco2,
            'Carbon_Price_USD_per_t': request.carbon_price_usd_per_t,
            'Compliance_Cost_USD': request.compliance_cost_usd,
        }])
        
        # Compute derived feature (same as training)
        input_data['Allowance_Gap_tCO2'] = (
            input_data['Emission_Produced_tCO2'] - input_data['Emission_Allowance_tCO2']
        )
        
        # Get feature columns in correct order
        feature_cols = (
            _trading_metadata['categorical_features'] + 
            _trading_metadata['numeric_features'] + 
            _trading_metadata['derived_features']
        )
        
        X = input_data[feature_cols]
        
        # Preprocess
        X_transformed = _trading_preprocessor.transform(X)
        
        # Predict
        prediction = _trading_model.predict(X_transformed)[0]
        probability = _trading_model.predict_proba(X_transformed)[0]
        
        # Map prediction to action
        action = "Buy" if prediction == 1 else "Sell"
        prob_value = float(probability[1] if prediction == 1 else probability[0])
        
        # Determine confidence level
        if prob_value >= 0.7:
            confidence = "High"
        elif prob_value >= 0.55:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        # Create input summary
        allowance_gap = request.emission_produced_tco2 - request.emission_allowance_tco2
        input_summary = {
            "industry": request.industry_type,
            "fuel": request.fuel_type,
            "allowance_gap_tco2": round(allowance_gap, 2),
            "carbon_price": round(request.carbon_price_usd_per_t, 2),
            "deficit_surplus": "Deficit" if allowance_gap > 0 else "Surplus"
        }
        
        return TradingPredictionResponse(
            predicted_action=action,
            probability=round(prob_value, 4),
            confidence=confidence,
            model_used=_trading_metadata['selected_model'],
            input_summary=input_summary
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
