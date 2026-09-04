"""
Database integration tests.

Tests database models, repositories, and data loading.
Requires PostgreSQL to be running and DATABASE_URL to be configured.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text
# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        from backend.database.database import SessionLocal
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        assert result == 1
        print("  [OK] Database connection successful")
        return True
    except Exception as e:
        print(f"  [FAIL] Database connection failed: {str(e)}")
        return False


def test_tables_exist():
    """Test that all tables exist."""
    print("Testing database tables...")
    try:
        from backend.database.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'market_data',
            'country_intelligence',
            'company_trading',
            'country_scores',
            'forecast_results',
            'scenario_results',
            'prediction_requests'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found"
            print(f"  [OK] Table '{table}' exists")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Table check failed: {str(e)}")
        return False


def test_market_repository():
    """Test MarketRepository."""
    print("Testing MarketRepository...")
    try:
        from backend.database.database import SessionLocal
        from backend.repositories.market_repository import MarketRepository
        
        db = SessionLocal()
        repo = MarketRepository(db)
        
        # Test getting timeseries
        timeseries = repo.get_timeseries()
        print(f"  [OK] Retrieved {len(timeseries)} market data points")
        
        # Test getting latest
        latest = repo.get_latest()
        if latest:
            print(f"  [OK] Latest year: {latest.year}, Value: ${latest.market_value}M")
        
        # Test getting forecast
        forecast = repo.get_forecast()
        print(f"  [OK] Retrieved {len(forecast)} forecast points")
        
        db.close()
        return True
    except Exception as e:
        print(f"  [FAIL] MarketRepository test failed: {str(e)}")
        return False


def test_country_repository():
    """Test CountryRepository."""
    print("Testing CountryRepository...")
    try:
        from backend.database.database import SessionLocal
        from backend.repositories.country_repository import CountryRepository
        
        db = SessionLocal()
        repo = CountryRepository(db)
        
        # Test getting all countries
        countries = repo.get_all_countries()
        print(f"  [OK] Retrieved {len(countries)} countries")
        
        # Test getting risk ranking
        risk_ranking = repo.get_risk_ranking(limit=5)
        if risk_ranking:
            top_risk = risk_ranking[0]
            print(f"  [OK] Top risk country: {top_risk.country} (score: {top_risk.risk_score})")
        
        # Test getting opportunity ranking
        opp_ranking = repo.get_opportunity_ranking(limit=5)
        if opp_ranking:
            top_opp = opp_ranking[0]
            print(f"  [OK] Top opportunity country: {top_opp.country} (score: {top_opp.opportunity_score})")
        
        # Test country exists
        exists = repo.country_exists("China")
        print(f"  [OK] Country exists check: China = {exists}")
        
        db.close()
        return True
    except Exception as e:
        print(f"  [FAIL] CountryRepository test failed: {str(e)}")
        return False


def test_trading_repository():
    """Test TradingRepository."""
    print("Testing TradingRepository...")
    try:
        from backend.database.database import SessionLocal
        from backend.repositories.trading_repository import TradingRepository
        
        db = SessionLocal()
        repo = TradingRepository(db)
        
        # Test getting transactions
        transactions = repo.get_all_transactions(limit=10)
        print(f"  [OK] Retrieved {len(transactions)} transactions")
        
        # Test saving prediction
        prediction = repo.save_prediction(
            industry_type="Energy",
            fuel_type="Renewable",
            verification_status="Verified",
            energy_demand_mwh=1000.0,
            emission_produced_tco2=500.0,
            emission_allowance_tco2=600.0,
            carbon_price_usd_per_t=50.0,
            compliance_cost_usd=5000.0,
            predicted_action="Buy",
            probability=0.75,
            confidence="High",
            model_used="LogisticRegression"
        )
        print(f"  [OK] Saved prediction: ID={prediction.id}, Action={prediction.predicted_action}")
        
        # Test getting prediction stats
        stats = repo.get_prediction_stats()
        print(f"  [OK] Prediction stats: {stats}")
        
        db.close()
        return True
    except Exception as e:
        print(f"  [FAIL] TradingRepository test failed: {str(e)}")
        return False


def test_scenario_repository():
    """Test ScenarioRepository."""
    print("Testing ScenarioRepository...")
    try:
        from backend.database.database import SessionLocal
        from backend.repositories.scenario_repository import ScenarioRepository
        
        db = SessionLocal()
        repo = ScenarioRepository(db)
        
        # Test saving scenario
        scenario = repo.save_scenario(
            carbon_price_change_pct=20.0,
            emissions_change_pct=-10.0,
            renewable_share_change_pct=15.0,
            gdp_growth_change_pct=5.0,
            baseline_market_value=535.0,
            baseline_market_volume=1950.0,
            scenario_market_value=550.0,
            scenario_market_volume=2100.0,
            value_change=15.0,
            value_change_pct=2.8,
            volume_change=150.0,
            volume_change_pct=7.7,
            model_info={"value_model": "Naive_LastValue", "volume_model": "XGBoost"},
            warnings=["Test scenario"]
        )
        print(f"  [OK] Saved scenario: ID={scenario.id}")
        
        # Test getting recent scenarios
        recent = repo.get_recent_scenarios(limit=5)
        print(f"  [OK] Retrieved {len(recent)} recent scenarios")
        
        # Test scenario stats
        stats = repo.get_scenario_stats()
        print(f"  [OK] Scenario stats: {stats}")
        
        db.close()
        return True
    except Exception as e:
        print(f"  [FAIL] ScenarioRepository test failed: {str(e)}")
        return False


def test_data_service_db():
    """Test DataServiceDB with database."""
    print("Testing DataServiceDB...")
    try:
        from backend.services.data_service_db import get_data_service_db
        
        service = get_data_service_db()
        
        # Check data source
        source = service.get_data_source()
        print(f"  [OK] Data source: {source}")
        
        # Test getting data
        df = service.get_global_market_timeseries()
        print(f"  [OK] Market timeseries: {len(df)} rows")
        
        countries = service.get_unique_countries()
        print(f"  [OK] Unique countries: {len(countries)}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] DataServiceDB test failed: {str(e)}")
        return False


def main():
    """Run all database tests."""
    print("=" * 60)
    print("DATABASE TESTS")
    print("=" * 60)
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("\n⚠ WARNING: DATABASE_URL not set")
        print("Database tests require PostgreSQL to be running.")
        print("\nTo run these tests:")
        print("1. Install and start PostgreSQL")
        print("2. Create database: createdb carbon_market")
        print("3. Set DATABASE_URL environment variable")
        print("4. Run migrations: alembic upgrade head")
        print("5. Seed database: python backend/scripts/seed_database.py")
        print("6. Re-run this test script")
        print("\n" + "=" * 60)
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Tables Exist", test_tables_exist()))
    results.append(("MarketRepository", test_market_repository()))
    results.append(("CountryRepository", test_country_repository()))
    results.append(("TradingRepository", test_trading_repository()))
    results.append(("ScenarioRepository", test_scenario_repository()))
    results.append(("DataServiceDB", test_data_service_db()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("-" * 60)
    
    if passed == total:
        print("🎉 ALL DATABASE TESTS PASSED!")
    else:
        print(f"⚠ {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
