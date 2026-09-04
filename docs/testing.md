# Testing Documentation

## Overview

This document describes the testing strategy and test results for the Carbon Market Intelligence platform.

## Test Levels

### 1. Unit Tests

**Phase 3 Model Validation** (`test_phase3_models.py`)
- ✓ Company trading model loads successfully
- ✓ Global market models load successfully
- ✓ All processed data files exist and are valid
- ✓ Model metadata is correct

**Results**: All tests pass

### 2. Integration Tests

**Backend API Tests** (`test_backend.py`)

Tests all 13 API endpoints with real data:

1. ✓ Health check endpoint
2. ✓ Market overview with KPIs
3. ✓ Market history (20 data points)
4. ✓ Market forecast (23 total points: 20 historical + 3 forecast)
5. ✓ Countries list with pagination
6. ✓ Country detail (China test case)
7. ✓ Risk ranking (Top: Saudi Arabia, Score: 86.82)
8. ✓ Opportunity ranking (Top: Costa Rica, Score: 83.13)
9. ✓ Trading model info (LogisticRegression, F1: 0.5422)
10. ✓ Trading prediction (valid input)
11. ✓ Scenario simulation (valid parameters)
12. ✓ Invalid scenario rejection (validation test)
13. ✓ Invalid country handling (404 test)

**Results**: All 13 tests pass

### 3. End-to-End Testing

**Manual Test Flows**

#### Flow 1: Market Analysis
```
1. Start backend: python run_backend.py
2. Verify backend: http://localhost:8000/docs
3. Check /api/health returns 200
4. Check /api/market/overview returns latest data (Year: 2024, Value: $535M)
5. Check /api/market/forecast returns 23 points
```

**Expected Result**: All market endpoints return valid data

#### Flow 2: Country Intelligence
```
1. GET /api/countries?limit=10
2. Verify 10 countries returned with risk/opportunity scores
3. GET /api/countries/China
4. Verify detailed country data returned
5. GET /api/countries/risk?limit=50
6. Verify risk ranking with scores
7. GET /api/countries/opportunity?limit=50
8. Verify opportunity ranking with scores
```

**Expected Result**: Country data loads with proper risk/opportunity scoring

#### Flow 3: Trading Prediction
```
1. GET /api/trading/model
2. Verify model metadata (F1: 0.5422, ROC-AUC: 0.5168)
3. POST /api/trading/predict with valid company data:
   {
     "industry_type": "Energy",
     "fuel_type": "Coal",
     "verification_status": "Verified",
     "energy_demand_mwh": 5000,
     "emission_produced_tco2": 3000,
     "emission_allowance_tco2": 2500,
     "carbon_price_usd_per_t": 50,
     "compliance_cost_usd": 10000
   }
4. Verify prediction returned (Buy/Sell with probability)
```

**Expected Result**: Model predicts Buy or Sell with confidence level

#### Flow 4: Scenario Simulation
```
1. POST /api/scenario/simulate with baseline (all 0% changes)
2. Verify baseline predictions returned
3. POST /api/scenario/simulate with scenario:
   {
     "carbon_price_change_pct": 50,
     "emissions_change_pct": -20,
     "renewable_share_change_pct": 40,
     "gdp_growth_change_pct": 5
   }
4. Verify scenario predictions differ from baseline
5. Check warnings array for interpretation guidance
```

**Expected Result**: Scenario shows impact on market volume (value uses Naive baseline)

#### Flow 5: Frontend Integration (Manual)
```
1. Install frontend dependencies: cd frontend && npm install
2. Start backend: python run_backend.py (port 8000)
3. Start frontend: npm run dev (port 3000)
4. Open browser: http://localhost:3000
5. Verify all tabs load:
   - Global Market tab shows KPIs and charts
   - Country Intelligence tab shows rankings
   - Trading Prediction tab shows form and predictions
   - Scenario Simulator tab shows sliders and results
6. Test interactions:
   - Search countries
   - View country detail
   - Submit trading prediction
   - Run scenario simulation
```

**Expected Result**: All UI components load data from backend

## Test Execution

### Run All Backend Tests

```bash
# Validate Phase 3 models
python test_phase3_models.py

# Test all API endpoints
python test_backend.py
```

### Manual End-to-End Test

```bash
# Terminal 1: Start backend
python run_backend.py

# Terminal 2: In a separate terminal, run backend tests
python test_backend.py

# Terminal 3: (Optional) Start frontend
cd frontend
npm install
npm run dev
```

## Test Results Summary

### Backend Tests
- **Total Tests**: 13
- **Passed**: 13
- **Failed**: 0
- **Coverage**: All required endpoints tested

### Model Tests
- **Phase 3 Models**: All load successfully
- **Processed Data**: All files present and valid
- **Predictions**: Models produce valid outputs

### Known Issues/Limitations

1. **Sklearn Version Warning**: Models trained with sklearn 1.9.0, current environment has 1.8.0. Works but shows warnings.

2. **Market Value Scenario**: Uses Naive_LastValue model, so scenario changes don't affect value predictions (documented limitation).

3. **Frontend Dependencies**: Requires npm install before first run. Installation may take 2-3 minutes.

4. **Model Performance**: Trading model F1 score is 0.54 (slight better than random), reflecting difficulty of the prediction task.

## Performance Benchmarks

### Backend Response Times (Approximate)
- Health check: <10ms
- Market overview: <50ms
- Market history: <50ms
- Market forecast: <50ms
- Countries list (50): <100ms
- Country detail: <50ms
- Risk ranking (50): <100ms
- Opportunity ranking (50): <100ms
- Trading prediction: <200ms (includes model inference)
- Scenario simulation: <300ms (includes XGBoost prediction)

### Data Loading
- Backend startup: ~2 seconds (loads all datasets and models into memory)
- Frontend initial load: <1 second (after npm install)

## Validation Checklist

Before demo:
- [ ] Backend starts without errors
- [ ] All API tests pass
- [ ] Frontend installs successfully
- [ ] Frontend connects to backend
- [ ] Charts render correctly
- [ ] All tabs functional
- [ ] Predictions return valid results
- [ ] Scenario simulation works
- [ ] Error states display properly
- [ ] Loading states display properly

## Continuous Testing

For development:
```bash
# Watch backend changes (auto-reload)
uvicorn backend.app.main:app --reload

# Watch frontend changes (auto-reload)
cd frontend && npm run dev
```

## Troubleshooting

### Backend Issues
**Error**: "Module not found"
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Error**: "XGBoost not found"
**Solution**: `pip install xgboost`

**Error**: "Port 8000 already in use"
**Solution**: Kill existing process or change port in run_backend.py

### Frontend Issues
**Error**: "Cannot find module"
**Solution**: Run `npm install` in frontend directory

**Error**: "API connection failed"
**Solution**: Ensure backend is running on port 8000

**Error**: "Plotly charts not rendering"
**Solution**: Check browser console for errors, ensure plotly.js is installed

## Test Data Integrity

### Raw Data Protection
- ✓ Raw data directory (`data/raw/`) is never modified
- ✓ All transformations write to `data/processed/`
- ✓ Original files remain unchanged

### Processed Data Validation
- ✓ All processed CSV files readable
- ✓ All JSON metadata valid
- ✓ No NaN values in required fields
- ✓ Data types correct

## Deployment Testing

For production deployment (future):
1. Run all unit tests
2. Run all integration tests
3. Build frontend: `cd frontend && npm run build`
4. Test production build: `npm run preview`
5. Load test backend with realistic traffic
6. Monitor memory usage during extended operation
7. Verify HTTPS configuration
8. Test CORS with production frontend URL
9. Validate authentication (if added)
10. Test error logging and monitoring

## Test Maintenance

**When to update tests:**
- Adding new endpoints
- Changing API schemas
- Updating model training
- Modifying processed data structure
- Adding new features

**Test data updates:**
- If new raw data added, update Phase 3 tests
- If model retrained, update expected metrics
- If data pipeline changes, regenerate processed files
