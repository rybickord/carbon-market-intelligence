# API Documentation

Complete reference for the Carbon Market Intelligence REST API.

**Base URL**: `http://localhost:8000`

**Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)

## Authentication

No authentication required for this hackathon version.

## Response Format

All responses return JSON.

### Success Response
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Health Endpoint

### GET /api/health

Health check endpoint.

**Response 200:**
```json
{
  "status": "healthy",
  "service": "Carbon Market Intelligence API",
  "version": "1.0.0"
}
```

## Market Endpoints

### GET /api/market/overview

Get global carbon market overview with latest statistics.

**Response 200:**
```json
{
  "latest_year": 2024,
  "latest_value": 535.0,
  "latest_volume": 84.0,
  "previous_value": 755.0,
  "previous_volume": 112.0,
  "value_growth_pct": -29.14,
  "volume_growth_pct": -25.0,
  "forecast_available": true
}
```

### GET /api/market/history

Get historical market data for charting.

**Response 200:**
```json
[
  {
    "year": 2005,
    "market_value": 48.0,
    "market_volume": 12.0
  },
  {
    "year": 2006,
    "market_value": 111.0,
    "market_volume": 32.0
  }
]
```

### GET /api/market/forecast

Get market forecast including historical and predicted values.

**Response 200:**
```json
[
  {
    "year": 2005,
    "market_value": 48.0,
    "market_volume": 12.0,
    "series": "historical",
    "value_model": null,
    "volume_model": null
  },
  {
    "year": 2025,
    "market_value": 535.0,
    "market_volume": 98.21,
    "series": "forecast",
    "value_model": "Naive_LastValue",
    "volume_model": "XGBoost"
  }
]
```

### GET /api/market/metrics

Get model evaluation metrics.

**Response 200:**
```json
{
  "Market_Value": {
    "selected_model": "Naive_LastValue",
    "walk_forward_metrics": {
      "Naive_LastValue": {
        "MAE": 563.3333,
        "RMSE": 807.7848,
        "R2": -0.3146,
        "MAPE": 54.7487,
        "n": 6
      }
    }
  },
  "Market_Volume": {
    "selected_model": "XGBoost",
    "walk_forward_metrics": { ... }
  }
}
```

## Country Endpoints

### GET /api/countries

Get list of countries with intelligence summary.

**Query Parameters:**
- `search` (optional): Search country by name
- `limit` (optional): Limit results (default: all, max: 500)

**Example:**
```
GET /api/countries?search=china&limit=10
```

**Response 200:**
```json
[
  {
    "country": "China",
    "iso": "CHN",
    "latest_year": 2021,
    "co2": 11472.369171,
    "per_capita_co2": 8.054722,
    "renewable_share": 28.53226,
    "risk_score": 75.23,
    "opportunity_score": 45.67
  }
]
```

### GET /api/countries/{country}

Get detailed information for a specific country.

**Path Parameters:**
- `country`: Country name (case-insensitive)

**Example:**
```
GET /api/countries/China
```

**Response 200:**
```json
{
  "country": "China",
  "iso": "CHN",
  "year": 2021,
  "co2": 11472.369171,
  "per_capita_co2": 8.054722,
  "renewable_share": 28.53226,
  "renewable_production": 2651.79,
  "gdp_growth": 8.45,
  "carbon_rate_2023": null,
  "risk_score": 75.23,
  "risk_category": "High",
  "opportunity_score": 45.67,
  "opportunity_category": "Moderate"
}
```

**Response 404:**
```json
{
  "detail": "Country 'InvalidCountry' not found"
}
```

### GET /api/countries/risk

Get country risk rankings (highest risk first).

**Query Parameters:**
- `limit` (optional): Limit results (default: 50, max: 500)

**Response 200:**
```json
[
  {
    "rank": 1,
    "country": "Saudi Arabia",
    "iso": "SAU",
    "risk_score": 86.82,
    "risk_category": "Very High",
    "co2": 672.264916,
    "per_capita_co2": 18.197731
  }
]
```

### GET /api/countries/opportunity

Get country opportunity rankings (highest opportunity first).

**Query Parameters:**
- `limit` (optional): Limit results (default: 50, max: 500)

**Response 200:**
```json
[
  {
    "rank": 1,
    "country": "Costa Rica",
    "iso": "CRI",
    "opportunity_score": 83.13,
    "opportunity_category": "Very High",
    "renewable_share": 99.24194,
    "gdp_growth": 7.6
  }
]
```

## Trading Endpoints

### GET /api/trading/model

Get trading model metadata and performance metrics.

**Response 200:**
```json
{
  "model_name": "LogisticRegression",
  "target": "Target_Trade_Action",
  "target_interpretation": "1 = Buy, 0 = Sell (matches Transaction_Type in source file)",
  "validation": "stratified 80/20 train/test split, random_state=42",
  "accuracy": 0.517,
  "precision": 0.5209,
  "recall": 0.5652,
  "f1_score": 0.5422,
  "roc_auc": 0.5168,
  "input_features": [
    "Industry_Type",
    "Fuel_Type",
    "Verification_Status",
    "Energy_Demand_MWh",
    "Emission_Produced_tCO2",
    "Emission_Allowance_tCO2",
    "Carbon_Price_USD_per_t",
    "Compliance_Cost_USD"
  ]
}
```

### POST /api/trading/predict

Predict whether a company should Buy or Sell carbon credits.

**Request Body:**
```json
{
  "industry_type": "Energy",
  "fuel_type": "Coal",
  "verification_status": "Verified",
  "energy_demand_mwh": 5000.0,
  "emission_produced_tco2": 3000.0,
  "emission_allowance_tco2": 2500.0,
  "carbon_price_usd_per_t": 50.0,
  "compliance_cost_usd": 10000.0
}
```

**Field Constraints:**
- `industry_type`: One of ["Cement", "Energy", "Manufacturing", "Steel"]
- `fuel_type`: One of ["Coal", "Mixed Fuel", "Natural Gas", "Renewable"]
- `verification_status`: One of ["Disputed", "Verified"]
- All numeric fields must be > 0 (except compliance_cost_usd >= 0)

**Response 200:**
```json
{
  "predicted_action": "Buy",
  "probability": 0.6234,
  "confidence": "Medium",
  "model_used": "LogisticRegression",
  "input_summary": {
    "industry": "Energy",
    "fuel": "Coal",
    "allowance_gap_tco2": 500.0,
    "carbon_price": 50.0,
    "deficit_surplus": "Deficit"
  }
}
```

**Response 400:**
```json
{
  "detail": "Invalid input: energy_demand_mwh must be greater than 0"
}
```

**Response 422:**
```json
{
  "detail": [
    {
      "loc": ["body", "industry_type"],
      "msg": "industry_type must be one of ['Cement', 'Energy', 'Manufacturing', 'Steel']",
      "type": "value_error"
    }
  ]
}
```

## Scenario Endpoint

### POST /api/scenario/simulate

Run a scenario simulation to compare baseline vs scenario predictions.

**Request Body:**
```json
{
  "carbon_price_change_pct": 50.0,
  "emissions_change_pct": -20.0,
  "renewable_share_change_pct": 30.0,
  "gdp_growth_change_pct": 5.0
}
```

**Field Constraints:**
- `carbon_price_change_pct`: -50 to +200
- `emissions_change_pct`: -30 to +50
- `renewable_share_change_pct`: -20 to +100
- `gdp_growth_change_pct`: -20 to +50

**Response 200:**
```json
{
  "baseline": {
    "market_value": 535.0,
    "market_volume": 98.21
  },
  "scenario": {
    "market_value": 535.0,
    "market_volume": 398.12
  },
  "changes": {
    "value_absolute": 0.0,
    "value_percent": 0.0,
    "volume_absolute": 299.91,
    "volume_percent": 305.36
  },
  "scenario_parameters": {
    "carbon_price_change_pct": 50.0,
    "emissions_change_pct": -20.0,
    "renewable_share_change_pct": 30.0,
    "gdp_growth_change_pct": 5.0
  },
  "model_info": {
    "market_value_model": "Naive_LastValue",
    "market_volume_model": "XGBoost",
    "baseline_year": 2024,
    "prediction_year": 2025,
    "limitations": [
      "Predictions are based on historical patterns and may not capture future structural changes",
      "Scenario changes are applied to lagged features as the model uses last-known values",
      "Carbon price is not directly modeled but may correlate with other factors",
      "Historical data contains only 20 annual observations"
    ]
  },
  "warnings": [
    "Market_Value uses Naive_LastValue baseline - scenario changes may not affect prediction",
    "Scenario shows extreme volume change (>100%) - interpret with caution"
  ]
}
```

**Response 400:**
```json
{
  "detail": "Invalid scenario parameters: emissions_change_pct must be between -30% and +50%"
}
```

**Response 422:**
```json
{
  "detail": [
    {
      "loc": ["body", "emissions_change_pct"],
      "msg": "ensure this value is greater than or equal to -30",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

## HTTP Status Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid input data
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

## Rate Limiting

No rate limiting in current version.

## CORS

Allowed origins:
- `http://localhost:3000`
- `http://localhost:5173`

## Examples

### Using curl

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Market Overview:**
```bash
curl http://localhost:8000/api/market/overview
```

**Country Detail:**
```bash
curl http://localhost:8000/api/countries/China
```

**Trading Prediction:**
```bash
curl -X POST http://localhost:8000/api/trading/predict \
  -H "Content-Type: application/json" \
  -d '{
    "industry_type": "Energy",
    "fuel_type": "Coal",
    "verification_status": "Verified",
    "energy_demand_mwh": 5000,
    "emission_produced_tco2": 3000,
    "emission_allowance_tco2": 2500,
    "carbon_price_usd_per_t": 50,
    "compliance_cost_usd": 10000
  }'
```

**Scenario Simulation:**
```bash
curl -X POST http://localhost:8000/api/scenario/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "emissions_change_pct": -20,
    "renewable_share_change_pct": 30,
    "gdp_growth_change_pct": 5,
    "carbon_price_change_pct": 50
  }'
```

### Using Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Get market overview
response = requests.get(f"{BASE_URL}/api/market/overview")
data = response.json()
print(f"Latest market value: ${data['latest_value']}M")

# Trading prediction
payload = {
    "industry_type": "Energy",
    "fuel_type": "Coal",
    "verification_status": "Verified",
    "energy_demand_mwh": 5000,
    "emission_produced_tco2": 3000,
    "emission_allowance_tco2": 2500,
    "carbon_price_usd_per_t": 50,
    "compliance_cost_usd": 10000
}
response = requests.post(f"{BASE_URL}/api/trading/predict", json=payload)
prediction = response.json()
print(f"Prediction: {prediction['predicted_action']}")

# Scenario simulation
scenario = {
    "emissions_change_pct": -20,
    "renewable_share_change_pct": 30,
    "gdp_growth_change_pct": 5,
    "carbon_price_change_pct": 50
}
response = requests.post(f"{BASE_URL}/api/scenario/simulate", json=scenario)
result = response.json()
print(f"Volume change: {result['changes']['volume_percent']:.2f}%")
```

### Using JavaScript (axios)

```javascript
import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

// Get market overview
const getMarketOverview = async () => {
  const response = await axios.get(`${BASE_URL}/api/market/overview`);
  console.log('Latest value:', response.data.latest_value);
};

// Trading prediction
const predictTrade = async () => {
  const payload = {
    industry_type: 'Energy',
    fuel_type: 'Coal',
    verification_status: 'Verified',
    energy_demand_mwh: 5000,
    emission_produced_tco2: 3000,
    emission_allowance_tco2: 2500,
    carbon_price_usd_per_t: 50,
    compliance_cost_usd: 10000
  };
  
  const response = await axios.post(`${BASE_URL}/api/trading/predict`, payload);
  console.log('Prediction:', response.data.predicted_action);
};

// Scenario simulation
const simulateScenario = async () => {
  const scenario = {
    emissions_change_pct: -20,
    renewable_share_change_pct: 30,
    gdp_growth_change_pct: 5,
    carbon_price_change_pct: 50
  };
  
  const response = await axios.post(`${BASE_URL}/api/scenario/simulate`, scenario);
  console.log('Volume change:', response.data.changes.volume_percent);
};
```

## Testing

API tests are available in `test_backend.py`. Run with:

```bash
python test_backend.py
```

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
- JSON: `http://localhost:8000/openapi.json`
- Interactive UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
