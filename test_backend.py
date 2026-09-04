"""
Quick test to ensure backend endpoints work correctly.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health():
    print("Testing /api/health...")
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    print(f"  ✓ Health check passed: {data}")


def test_market_overview():
    print("\nTesting /api/market/overview...")
    response = client.get("/api/market/overview")
    assert response.status_code == 200
    data = response.json()
    assert 'latest_year' in data
    assert 'latest_value' in data
    print(f"  ✓ Market overview: Year={data['latest_year']}, Value=${data['latest_value']}M")


def test_market_history():
    print("\nTesting /api/market/history...")
    response = client.get("/api/market/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    print(f"  ✓ Market history: {len(data)} data points")


def test_market_forecast():
    print("\nTesting /api/market/forecast...")
    response = client.get("/api/market/forecast")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    historical = [p for p in data if p['series'] == 'historical']
    forecast = [p for p in data if p['series'] == 'forecast']
    print(f"  ✓ Forecast: {len(historical)} historical, {len(forecast)} forecast points")


def test_countries_list():
    print("\nTesting /api/countries...")
    response = client.get("/api/countries?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    print(f"  ✓ Countries list: {len(data)} countries")


def test_country_detail():
    print("\nTesting /api/countries/{country}...")
    response = client.get("/api/countries/China")
    assert response.status_code == 200
    data = response.json()
    assert data['country'] == 'China'
    print(f"  ✓ Country detail: {data['country']}, CO2={data['co2']}")


def test_risk_ranking():
    print("\nTesting /api/countries/risk...")
    response = client.get("/api/countries/risk?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    top = data[0]
    print(f"  ✓ Risk ranking: Top={top['country']}, Score={top['risk_score']}")


def test_opportunity_ranking():
    print("\nTesting /api/countries/opportunity...")
    response = client.get("/api/countries/opportunity?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    top = data[0]
    print(f"  ✓ Opportunity ranking: Top={top['country']}, Score={top['opportunity_score']}")


def test_trading_model():
    print("\nTesting /api/trading/model...")
    response = client.get("/api/trading/model")
    assert response.status_code == 200
    data = response.json()
    assert 'model_name' in data
    assert 'f1_score' in data
    print(f"  ✓ Trading model: {data['model_name']}, F1={data['f1_score']}")


def test_trading_prediction():
    print("\nTesting /api/trading/predict...")
    payload = {
        "industry_type": "Energy",
        "fuel_type": "Coal",
        "verification_status": "Verified",
        "energy_demand_mwh": 5000.0,
        "emission_produced_tco2": 3000.0,
        "emission_allowance_tco2": 2500.0,
        "carbon_price_usd_per_t": 50.0,
        "compliance_cost_usd": 10000.0
    }
    response = client.post("/api/trading/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['predicted_action'] in ['Buy', 'Sell']
    print(f"  ✓ Trading prediction: {data['predicted_action']} (confidence={data['confidence']})")


def test_scenario_simulation():
    print("\nTesting /api/scenario/simulate...")
    payload = {
        "carbon_price_change_pct": 20.0,
        "emissions_change_pct": -10.0,
        "renewable_share_change_pct": 30.0,
        "gdp_growth_change_pct": 5.0
    }
    response = client.post("/api/scenario/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'baseline' in data
    assert 'scenario' in data
    assert 'changes' in data
    print(f"  ✓ Scenario simulation:")
    print(f"    Baseline Value: ${data['baseline']['market_value']}M")
    print(f"    Scenario Value: ${data['scenario']['market_value']}M")
    print(f"    Volume Change: {data['changes']['volume_percent']:+.2f}%")


def test_invalid_scenario():
    print("\nTesting /api/scenario/simulate (invalid)...")
    payload = {
        "emissions_change_pct": 100.0  # Out of range
    }
    response = client.post("/api/scenario/simulate", json=payload)
    assert response.status_code == 422  # Validation error
    print(f"  ✓ Validation correctly rejected invalid input")


def test_invalid_country():
    print("\nTesting /api/countries/{invalid}...")
    response = client.get("/api/countries/InvalidCountryXYZ")
    assert response.status_code == 404
    print(f"  ✓ Correctly returned 404 for invalid country")


if __name__ == "__main__":
    print("="*60)
    print("Backend API Tests")
    print("="*60)
    
    try:
        test_health()
        test_market_overview()
        test_market_history()
        test_market_forecast()
        test_countries_list()
        test_country_detail()
        test_risk_ranking()
        test_opportunity_ranking()
        test_trading_model()
        test_trading_prediction()
        test_scenario_simulation()
        test_invalid_scenario()
        test_invalid_country()
        
        print("\n" + "="*60)
        print("✓ ALL BACKEND TESTS PASSED")
        print("="*60)
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
