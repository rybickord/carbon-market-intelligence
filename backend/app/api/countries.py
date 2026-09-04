"""
Countries endpoints for country intelligence, risk, and opportunity data.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from backend.app.schemas import (
    CountryListItem, 
    CountryDetail, 
    CountryRiskItem, 
    CountryOpportunityItem
)
from backend.services.data_service import get_data_service

router = APIRouter()
data_service = get_data_service()


@router.get("", response_model=List[CountryListItem])
async def get_countries(
    search: Optional[str] = Query(None, description="Search country by name"),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Limit results")
):
    """
    Get list of countries with intelligence summary.
    """
    try:
        intel = data_service.get_country_intelligence()
        risk = data_service.get_country_risk_scores()
        opp = data_service.get_country_opportunity_scores()
        
        # Get latest year per country
        latest = intel.sort_values('Year', ascending=False).groupby('Country').first().reset_index()
        
        # Merge with risk and opportunity scores
        latest = latest.merge(
            risk[['Country', 'Risk_Score']],
            on='Country',
            how='left'
        )
        latest = latest.merge(
            opp[['Country', 'Opportunity_Score']],
            on='Country',
            how='left'
        )
        
        # Apply search filter
        if search:
            latest = latest[latest['Country'].str.contains(search, case=False, na=False)]
        
        # Apply limit
        if limit:
            latest = latest.head(limit)
        
        results = []
        for _, row in latest.iterrows():
            results.append(CountryListItem(
                country=row['Country'],
                iso=row['ISO'] if pd.notna(row['ISO']) else None,
                latest_year=int(row['Year']),
                co2=float(row['CO2']) if pd.notna(row['CO2']) else None,
                per_capita_co2=float(row['Per_Capita_CO2']) if pd.notna(row['Per_Capita_CO2']) else None,
                renewable_share=float(row['Renewable_Electricity_Share']) if pd.notna(row['Renewable_Electricity_Share']) else None,
                risk_score=float(row['Risk_Score']) if pd.notna(row['Risk_Score']) else None,
                opportunity_score=float(row['Opportunity_Score']) if pd.notna(row['Opportunity_Score']) else None
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching countries: {str(e)}")


@router.get("/risk", response_model=List[CountryRiskItem])
async def get_country_risk_ranking(
    limit: Optional[int] = Query(50, ge=1, le=500, description="Limit results")
):
    """
    Get country risk rankings (highest risk first).
    """
    try:
        df = data_service.get_country_risk_scores()
        df = df.sort_values('Risk_Score', ascending=False)
        
        if limit:
            df = df.head(limit)
        
        results = []
        for rank, (_, row) in enumerate(df.iterrows(), start=1):
            results.append(CountryRiskItem(
                rank=rank,
                country=row['Country'],
                iso=row['ISO'] if pd.notna(row['ISO']) else None,
                risk_score=float(row['Risk_Score']),
                risk_category=row['Risk_Category'],
                co2=float(row['CO2']) if pd.notna(row['CO2']) else None,
                per_capita_co2=float(row['Per_Capita_CO2']) if pd.notna(row['Per_Capita_CO2']) else None
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching risk rankings: {str(e)}")


@router.get("/opportunity", response_model=List[CountryOpportunityItem])
async def get_country_opportunity_ranking(
    limit: Optional[int] = Query(50, ge=1, le=500, description="Limit results")
):
    """
    Get country opportunity rankings (highest opportunity first).
    """
    try:
        df = data_service.get_country_opportunity_scores()
        df = df.sort_values('Opportunity_Score', ascending=False)
        
        if limit:
            df = df.head(limit)
        
        results = []
        for rank, (_, row) in enumerate(df.iterrows(), start=1):
            results.append(CountryOpportunityItem(
                rank=rank,
                country=row['Country'],
                iso=row['ISO'] if pd.notna(row['ISO']) else None,
                opportunity_score=float(row['Opportunity_Score']),
                opportunity_category=row['Opportunity_Category'],
                renewable_share=float(row['Renewable_Electricity_Share']) if pd.notna(row['Renewable_Electricity_Share']) else None,
                gdp_growth=float(row['GDP_Growth']) if pd.notna(row['GDP_Growth']) else None
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching opportunity rankings: {str(e)}")


@router.get("/{country}", response_model=CountryDetail)
async def get_country_detail(country: str):
    """
    Get detailed information for a specific country.
    """
    try:
        detail = data_service.get_country_detail(country)
        
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Country '{country}' not found")
        
        return CountryDetail(**detail)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching country detail: {str(e)}")
