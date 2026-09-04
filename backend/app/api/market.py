"""
Market endpoints for global carbon market data.
"""

from typing import List
from fastapi import APIRouter, HTTPException
import pandas as pd

from backend.app.schemas import MarketOverview, MarketHistoryPoint, MarketForecastPoint
from backend.services.data_service import get_data_service

router = APIRouter()
data_service = get_data_service()


@router.get("/overview", response_model=MarketOverview)
async def get_market_overview():
    """
    Get global carbon market overview with latest statistics.
    """
    try:
        df = data_service.get_global_market_timeseries()
        df = df.sort_values('Year')
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No market data available")
        
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else None
        
        # Calculate growth rates
        value_growth = None
        volume_growth = None
        
        if previous is not None:
            if previous['Market_Value'] > 0:
                value_growth = ((latest['Market_Value'] - previous['Market_Value']) / 
                               previous['Market_Value'] * 100)
            if previous['Market_Volume'] > 0:
                volume_growth = ((latest['Market_Volume'] - previous['Market_Volume']) / 
                                previous['Market_Volume'] * 100)
        
        return MarketOverview(
            latest_year=int(latest['Year']),
            latest_value=float(latest['Market_Value']),
            latest_volume=float(latest['Market_Volume']),
            previous_value=float(previous['Market_Value']) if previous is not None else None,
            previous_volume=float(previous['Market_Volume']) if previous is not None else None,
            value_growth_pct=round(value_growth, 2) if value_growth is not None else None,
            volume_growth_pct=round(volume_growth, 2) if volume_growth is not None else None,
            forecast_available=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market overview: {str(e)}")


@router.get("/history", response_model=List[MarketHistoryPoint])
async def get_market_history():
    """
    Get historical market data for charting.
    """
    try:
        df = data_service.get_global_market_timeseries()
        df = df.sort_values('Year')
        
        return [
            MarketHistoryPoint(
                year=int(row['Year']),
                market_value=float(row['Market_Value']),
                market_volume=float(row['Market_Volume'])
            )
            for _, row in df.iterrows()
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market history: {str(e)}")


@router.get("/forecast", response_model=List[MarketForecastPoint])
async def get_market_forecast():
    """
    Get market forecast including historical and predicted values.
    """
    try:
        df = data_service.get_global_market_forecast()
        df = df.sort_values('Year')
        
        results = []
        for _, row in df.iterrows():
            point = MarketForecastPoint(
                year=int(row['Year']),
                market_value=float(row['Market_Value']),
                market_volume=float(row['Market_Volume']),
                series=row['Series']
            )
            
            # Add model info for forecast points
            if row['Series'] == 'forecast':
                if 'Market_Value_model' in row and pd.notna(row['Market_Value_model']):
                    point.value_model = row['Market_Value_model']
                if 'Market_Volume_model' in row and pd.notna(row['Market_Volume_model']):
                    point.volume_model = row['Market_Volume_model']
            
            results.append(point)
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market forecast: {str(e)}")


@router.get("/metrics")
async def get_market_metrics():
    """
    Get model evaluation metrics for market forecasting.
    """
    try:
        metrics = data_service.get_global_market_metrics()
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market metrics: {str(e)}")
