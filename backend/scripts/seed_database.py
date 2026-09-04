"""
Database seeding script.

Loads data from processed CSV files into PostgreSQL database.
Safe to run multiple times (idempotent where practical).
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.database.database import SessionLocal, engine
from backend.database.models import (
    Base,
    MarketData,
    CountryIntelligence,
    CompanyTrading,
    CountryScore,
    ForecastResult,
)

PROCESSED_DIR = ROOT / "data" / "processed"


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def seed_market_data(db: Session):
    """Load global market timeseries data."""
    print("\nSeeding market_data...")
    
    csv_path = PROCESSED_DIR / "global_market_timeseries.csv"
    df = pd.read_csv(csv_path)
    
    added = 0
    skipped = 0
    
    for _, row in df.iterrows():
        # Check if year already exists
        existing = db.query(MarketData).filter(MarketData.year == int(row['Year'])).first()
        if existing:
            skipped += 1
            continue
        
        record = MarketData(
            year=int(row['Year']),
            market_value=float(row['Market_Value']),
            market_volume=float(row['Market_Volume']),
            global_co2=float(row['Global_CO2']) if pd.notna(row['Global_CO2']) else None,
            renewable_electricity_share=float(row['Renewable_Electricity_Share']) if pd.notna(row['Renewable_Electricity_Share']) else None,
            renewable_production=float(row['Renewable_Production']) if pd.notna(row['Renewable_Production']) else None,
            global_gdp_growth=float(row['Global_GDP_Growth']) if pd.notna(row['Global_GDP_Growth']) else None,
        )
        db.add(record)
        added += 1
    
    db.commit()
    print(f"✓ Market data: {added} added, {skipped} skipped")


def seed_country_intelligence(db: Session):
    """Load country intelligence data."""
    print("\nSeeding country_intelligence...")
    
    csv_path = PROCESSED_DIR / "country_intelligence.csv"
    df = pd.read_csv(csv_path)
    
    added = 0
    skipped = 0
    
    for _, row in df.iterrows():
        # Check if country-year combination already exists
        existing = db.query(CountryIntelligence).filter(
            CountryIntelligence.country == row['Country'],
            CountryIntelligence.year == int(row['Year'])
        ).first()
        
        if existing:
            skipped += 1
            continue
        
        record = CountryIntelligence(
            country=row['Country'],
            iso=row['ISO'] if pd.notna(row['ISO']) else None,
            year=int(row['Year']),
            co2=float(row['CO2']) if pd.notna(row['CO2']) else None,
            per_capita_co2=float(row['Per_Capita_CO2']) if pd.notna(row['Per_Capita_CO2']) else None,
            renewable_electricity_share=float(row['Renewable_Electricity_Share']) if pd.notna(row['Renewable_Electricity_Share']) else None,
            renewable_production=float(row['Renewable_Production']) if pd.notna(row['Renewable_Production']) else None,
            gdp_growth=float(row['GDP_Growth']) if pd.notna(row['GDP_Growth']) else None,
            carbon_rate_2023=float(row['Carbon_Rate_2023']) if pd.notna(row['Carbon_Rate_2023']) else None,
        )
        db.add(record)
        added += 1
        
        # Commit in batches to avoid memory issues
        if added % 1000 == 0:
            db.commit()
            print(f"  Progress: {added} records added...")
    
    db.commit()
    print(f"✓ Country intelligence: {added} added, {skipped} skipped")


def seed_company_trading(db: Session):
    """Load company trading dataset."""
    print("\nSeeding company_trading...")
    
    csv_path = PROCESSED_DIR / "company_trading_dataset.csv"
    df = pd.read_csv(csv_path)
    
    # Check if any records exist
    count = db.query(CompanyTrading).count()
    if count > 0:
        print(f"✓ Company trading: {count} records already exist, skipping bulk load")
        return
    
    added = 0
    
    for _, row in df.iterrows():
        record = CompanyTrading(
            company_id=row['Company_ID'],
            industry_type=row['Industry_Type'],
            date=pd.to_datetime(row['Date']),
            energy_demand_mwh=float(row['Energy_Demand_MWh']),
            fuel_type=row['Fuel_Type'],
            emission_produced_tco2=float(row['Emission_Produced_tCO2']),
            emission_allowance_tco2=float(row['Emission_Allowance_tCO2']),
            carbon_price_usd_per_t=float(row['Carbon_Price_USD_per_t']),
            transaction_type=row['Transaction_Type'],
            credits_traded_tco2=float(row['Credits_Traded_tCO2']),
            verification_status=row['Verification_Status'],
            compliance_cost_usd=float(row['Compliance_Cost_USD']),
            optimization_scenario=row['Optimization_Scenario'] if pd.notna(row['Optimization_Scenario']) else None,
            carbon_cost_savings_usd=float(row['Carbon_Cost_Savings_USD']) if pd.notna(row['Carbon_Cost_Savings_USD']) else None,
            target_trade_action=int(row['Target_Trade_Action']) if pd.notna(row['Target_Trade_Action']) else None,
        )
        db.add(record)
        added += 1
        
        # Commit in batches
        if added % 1000 == 0:
            db.commit()
            print(f"  Progress: {added} records added...")
    
    db.commit()
    print(f"✓ Company trading: {added} added")


def seed_country_scores(db: Session):
    """Load country risk and opportunity scores."""
    print("\nSeeding country_scores...")
    
    risk_csv = PROCESSED_DIR / "country_risk_scores.csv"
    opp_csv = PROCESSED_DIR / "country_opportunity_scores.csv"
    
    risk_df = pd.read_csv(risk_csv)
    opp_df = pd.read_csv(opp_csv)
    
    # Merge on country and year
    merged = pd.merge(
        risk_df,
        opp_df,
        on=['Country', 'ISO', 'Year'],
        how='outer',
        suffixes=('_risk', '_opp')
    )
    
    added = 0
    skipped = 0
    
    for _, row in merged.iterrows():
        # Check if country-year combination already exists
        existing = db.query(CountryScore).filter(
            CountryScore.country == row['Country'],
            CountryScore.year == int(row['Year'])
        ).first()
        
        if existing:
            skipped += 1
            continue
        
        record = CountryScore(
            country=row['Country'],
            iso=row['ISO'] if pd.notna(row['ISO']) else None,
            year=int(row['Year']),
            # Risk scores
            risk_score=float(row['Risk_Score']) if pd.notna(row['Risk_Score']) else None,
            risk_category=row['Risk_Category'] if pd.notna(row['Risk_Category']) else None,
            comp_co2=float(row['comp_CO2']) if 'comp_CO2' in row and pd.notna(row['comp_CO2']) else None,
            comp_per_cap=float(row['comp_PerCap']) if 'comp_PerCap' in row and pd.notna(row['comp_PerCap']) else None,
            comp_renew_weak=float(row['comp_RenewWeak']) if 'comp_RenewWeak' in row and pd.notna(row['comp_RenewWeak']) else None,
            comp_gdp_weak=float(row['comp_GDPWeak']) if 'comp_GDPWeak' in row and pd.notna(row['comp_GDPWeak']) else None,
            comp_policy_weak=float(row['comp_PolicyWeak']) if 'comp_PolicyWeak' in row and pd.notna(row['comp_PolicyWeak']) else None,
            # Opportunity scores
            opportunity_score=float(row['Opportunity_Score']) if pd.notna(row['Opportunity_Score']) else None,
            opportunity_category=row['Opportunity_Category'] if pd.notna(row['Opportunity_Category']) else None,
            comp_renew_elec=float(row['comp_RenewElec']) if 'comp_RenewElec' in row and pd.notna(row['comp_RenewElec']) else None,
            comp_renew_prod=float(row['comp_RenewProd']) if 'comp_RenewProd' in row and pd.notna(row['comp_RenewProd']) else None,
            comp_transition=float(row['comp_Transition']) if 'comp_Transition' in row and pd.notna(row['comp_Transition']) else None,
            comp_econ_res=float(row['comp_EconRes']) if 'comp_EconRes' in row and pd.notna(row['comp_EconRes']) else None,
            comp_policy_enable=float(row['comp_PolicyEnable']) if 'comp_PolicyEnable' in row and pd.notna(row['comp_PolicyEnable']) else None,
            # Flags
            flag_renewable_imputed=str(row['Flag_Renewable_Imputed']) if 'Flag_Renewable_Imputed' in row and pd.notna(row['Flag_Renewable_Imputed']) else None,
            flag_gdp_imputed=str(row['Flag_GDP_Imputed']) if 'Flag_GDP_Imputed' in row and pd.notna(row['Flag_GDP_Imputed']) else None,
            flag_carbon_rate_imputed=str(row['Flag_CarbonRate_Imputed']) if 'Flag_CarbonRate_Imputed' in row and pd.notna(row['Flag_CarbonRate_Imputed']) else None,
            flag_renew_elec_imputed=str(row['Flag_RenewElec_Imputed']) if 'Flag_RenewElec_Imputed' in row and pd.notna(row['Flag_RenewElec_Imputed']) else None,
            flag_renew_prod_imputed=str(row['Flag_RenewProd_Imputed']) if 'Flag_RenewProd_Imputed' in row and pd.notna(row['Flag_RenewProd_Imputed']) else None,
        )
        db.add(record)
        added += 1
        
        # Commit in batches
        if added % 1000 == 0:
            db.commit()
            print(f"  Progress: {added} records added...")
    
    db.commit()
    print(f"✓ Country scores: {added} added, {skipped} skipped")


def seed_forecast_results(db: Session):
    """Load forecast results (historical + future predictions)."""
    print("\nSeeding forecast_results...")
    
    csv_path = PROCESSED_DIR / "global_market_forecast.csv"
    df = pd.read_csv(csv_path)
    
    added = 0
    skipped = 0
    
    for _, row in df.iterrows():
        # Check if year already exists
        existing = db.query(ForecastResult).filter(ForecastResult.year == int(row['Year'])).first()
        if existing:
            skipped += 1
            continue
        
        record = ForecastResult(
            year=int(row['Year']),
            market_value=float(row['Market_Value']),
            market_volume=float(row['Market_Volume']),
            series=row['Series'],
            market_value_model=row['Market_Value_model'] if pd.notna(row['Market_Value_model']) else None,
            market_volume_model=row['Market_Volume_model'] if pd.notna(row['Market_Volume_model']) else None,
        )
        db.add(record)
        added += 1
    
    db.commit()
    print(f"✓ Forecast results: {added} added, {skipped} skipped")


def main():
    """Run database seeding."""
    print("=" * 60)
    print("CARBON MARKET INTELLIGENCE - DATABASE SEEDING")
    print("=" * 60)
    
    try:
        # Test database connection
        print("\nTesting database connection...")
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✓ Database connection successful")
        
        # Create tables
        create_tables()
        
        # Seed data
        db = SessionLocal()
        try:
            seed_market_data(db)
            seed_country_intelligence(db)
            seed_company_trading(db)
            seed_country_scores(db)
            seed_forecast_results(db)
            
            print("\n" + "=" * 60)
            print("✓ DATABASE SEEDING COMPLETE")
            print("=" * 60)
            
        finally:
            db.close()
    
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. DATABASE_URL environment variable is set correctly")
        print("3. Database exists and is accessible")
        print("\nExample DATABASE_URL:")
        print("  postgresql+psycopg://username:password@localhost:5432/carbon_market")
        sys.exit(1)


if __name__ == "__main__":
    main()
