# System Architecture

## Overview

Carbon Market Intelligence is a full-stack web application that combines data processing, machine learning, REST API, and interactive visualization to provide carbon market analysis and predictions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         React Application (Port 3000)                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐           │ │
│  │  │Dashboard │  │ Country  │  │ Trading   │           │ │
│  │  │          │  │Intelligence│  │ Predictor │           │ │
│  │  └──────────┘  └──────────┘  └───────────┘           │ │
│  │  ┌──────────┐  ┌──────────────────────────┐          │ │
│  │  │ Market   │  │  Scenario Simulator       │          │ │
│  │  │ Overview │  │                            │          │ │
│  │  └──────────┘  └──────────────────────────┘          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST (Axios)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        FastAPI Application (Port 8000)                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │ Market   │  │ Countries│  │ Trading  │            │ │
│  │  │ Endpoints│  │ Endpoints│  │ Endpoints│            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  │  ┌──────────────────────────────────────┐            │ │
│  │  │     Scenario Endpoint                 │            │ │
│  │  └──────────────────────────────────────┘            │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                       Service Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Data Service (Singleton)                    │ │
│  │  - Load and cache all processed datasets               │ │
│  │  - Provide data access methods                         │ │
│  │  - In-memory caching for performance                   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                         ML Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Global Market   │  │ Company Trading │                  │
│  │ Models          │  │ Classifier      │                  │
│  │ - Naive_LastValue│  │ - LogisticReg  │                  │
│  │ - XGBoost       │  │ - Preprocessor │                  │
│  └─────────────────┘  └─────────────────┘                  │
│  ┌─────────────────────────────────────────────┐           │
│  │      Scenario Simulator                     │           │
│  │  - Load models and historical data          │           │
│  │  - Apply scenario parameters                │           │
│  │  - Generate predictions                     │           │
│  └─────────────────────────────────────────────┘           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Processed Data (CSV/JSON)                    │ │
│  │  - global_market_timeseries.csv                        │ │
│  │  - global_market_forecast.csv                          │ │
│  │  - country_intelligence.csv                            │ │
│  │  - country_risk_scores.csv                             │ │
│  │  - country_opportunity_scores.csv                      │ │
│  │  - company_trading_dataset.csv                         │ │
│  │  - Model metadata (JSON)                               │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        Raw Data (Protected, Read-Only)                 │ │
│  │  - Voluntary carbon market data                        │ │
│  │  - CO2 emissions by country                            │ │
│  │  - Renewable energy statistics                         │ │
│  │  - GDP growth data                                     │ │
│  │  - OECD carbon pricing                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React + Vite)

**Technology Stack:**
- React 18 (UI framework)
- Vite (build tool & dev server)
- Tailwind CSS (styling)
- Plotly.js (charting)
- Axios (HTTP client)

**Key Components:**
- `Dashboard.jsx`: Main container with tab navigation
- `MarketOverview.jsx`: KPI cards for latest market statistics
- `MarketCharts.jsx`: Time series charts with Plotly
- `CountryIntelligence.jsx`: Risk/opportunity rankings and search
- `TradingPredictor.jsx`: Trading prediction form and results
- `ScenarioSimulator.jsx`: Interactive scenario controls and comparison

**API Service Layer:**
- Centralized API client in `services/api.js`
- Axios instance with base URL configuration
- Organized API methods by domain (market, countries, trading, scenario)

**State Management:**
- Component-level state with React hooks
- No global state management (not needed for current complexity)
- Loading and error states handled per component

### Backend (FastAPI)

**Technology Stack:**
- FastAPI (web framework)
- Pydantic (data validation)
- uvicorn (ASGI server)
- Python 3.8+

**API Structure:**
```
/api/health                    # Health check
/api/market/overview           # Market KPIs
/api/market/history            # Historical data
/api/market/forecast           # Forecast with historical
/api/market/metrics            # Model metrics
/api/countries                 # List countries
/api/countries/{country}       # Country detail
/api/countries/risk            # Risk ranking
/api/countries/opportunity     # Opportunity ranking
/api/trading/model             # Model info
/api/trading/predict           # Prediction
/api/scenario/simulate         # Scenario simulation
```

**Key Features:**
- OpenAPI/Swagger documentation at `/docs`
- CORS middleware for frontend communication
- Pydantic schemas for request/response validation
- Centralized error handling
- Data caching via singleton DataService

### Service Layer

**DataService (Singleton Pattern):**
- Loads all processed datasets on startup
- Caches data in memory for fast access
- Provides clean interface for data access
- Handles data transformations (filtering, aggregation)

**Benefits:**
- No repeated file I/O
- Fast API response times (<100ms for most endpoints)
- Centralized data management
- Easy to extend with new datasets

### ML Layer

**Global Market Models:**
- Location: `ml/models/global_market/`
- Market Value: Naive_LastValue (simple baseline)
- Market Volume: XGBoost regressor
- Features: Lagged market values, macro indicators
- Validation: Walk-forward cross-validation

**Company Trading Classifier:**
- Location: `ml/models/company_trading/`
- Model: Logistic Regression
- Preprocessor: ColumnTransformer (OneHotEncoder + StandardScaler)
- Features: Industry, fuel, verification status, emissions, allowance, price
- Target: Buy (1) vs Sell (0)

**Scenario Simulator:**
- Python class: `ml/scenario_simulator.py`
- Loads models and historical data
- Modifies features based on scenario parameters
- Generates baseline and scenario predictions
- Returns structured comparison with warnings

**Model Loading:**
- Models loaded once at application startup
- Stored in module-level variables
- Fast inference (<200ms per prediction)

### Data Layer

**Processed Data:**
- Format: CSV for tabular data, JSON for metadata
- Location: `data/processed/`
- Update frequency: Static (generated during Phase 3)
- Size: ~1.5 MB total

**Raw Data:**
- Format: CSV, XLSX, PDF
- Location: `data/raw/`
- Protection: Never modified by application
- Purpose: Source of truth for reprocessing

## Data Flow

### 1. Market Overview Request

```
User clicks "Global Market" tab
  ↓
React component (MarketOverview.jsx)
  ↓
API call: GET /api/market/overview
  ↓
FastAPI endpoint handler
  ↓
DataService.get_global_market_timeseries()
  ↓
Cached DataFrame in memory
  ↓
Calculate KPIs (latest value, YoY growth)
  ↓
Pydantic response model (MarketOverview)
  ↓
JSON response to frontend
  ↓
React updates component state
  ↓
UI renders with new data
```

### 2. Trading Prediction Request

```
User fills form and clicks "Predict"
  ↓
React component (TradingPredictor.jsx)
  ↓
API call: POST /api/trading/predict
  ↓
FastAPI endpoint handler
  ↓
Pydantic validation (TradingPredictionRequest)
  ↓
Load preprocessor and model (cached)
  ↓
Build input DataFrame with derived features
  ↓
Transform features with preprocessor
  ↓
Model prediction + probability
  ↓
Pydantic response (TradingPredictionResponse)
  ↓
JSON response to frontend
  ↓
React displays prediction with confidence
```

### 3. Scenario Simulation Request

```
User adjusts sliders and clicks "Run Simulation"
  ↓
React component (ScenarioSimulator.jsx)
  ↓
API call: POST /api/scenario/simulate
  ↓
FastAPI endpoint handler
  ↓
Pydantic validation (ScenarioRequest)
  ↓
Create ScenarioParameters object
  ↓
ScenarioSimulator.simulate()
  ↓
Load historical data and models
  ↓
Build baseline features (no changes)
  ↓
Build scenario features (with changes)
  ↓
Predict both scenarios
  ↓
Calculate differences and generate warnings
  ↓
Pydantic response (ScenarioResponse)
  ↓
JSON response to frontend
  ↓
React displays baseline vs scenario comparison
```

## Security Considerations

### Current Implementation
- CORS restricted to localhost origins
- No authentication/authorization (demo/hackathon scope)
- Input validation via Pydantic
- No SQL injection risk (no database)
- No XSS risk (React escapes by default)

### Production Recommendations
- Add authentication (JWT tokens)
- Rate limiting on API endpoints
- HTTPS only
- Environment-based configuration
- Secrets management
- API key for external clients
- Input sanitization for file uploads
- Logging and monitoring

## Performance

### Backend
- Startup time: ~2 seconds (data + model loading)
- Health check: <10ms
- Market endpoints: 20-50ms
- Country endpoints: 50-100ms
- Trading prediction: ~150ms
- Scenario simulation: ~250ms

### Frontend
- Initial load: <1 second (after build)
- Component render: <50ms
- Chart rendering: 100-200ms (Plotly)
- API call overhead: 50-100ms (local)

### Optimization Strategies
- Data cached in memory (DataService)
- Models loaded once at startup
- Frontend code splitting (Vite)
- Plotly config for performance
- Lazy component loading (future)

## Scalability

### Current Limitations
- Single-process server
- In-memory data cache
- No horizontal scaling
- No load balancing

### Future Improvements
- Database backend (PostgreSQL)
- Redis for caching
- Multiple workers (Gunicorn)
- Load balancer (Nginx)
- Containerization (Docker)
- Cloud deployment (AWS/Azure/GCP)
- CDN for frontend assets

## Deployment

### Development
```bash
# Backend
python run_backend.py

# Frontend
cd frontend && npm run dev
```

### Production (Recommended)
```bash
# Backend
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
npm run build
# Serve dist/ with Nginx or similar
```

## Monitoring

### Health Checks
- `/api/health` endpoint returns service status
- Can be used by load balancers/monitoring tools

### Logging
- FastAPI automatic logging
- Console output for development
- Production: structured logs to file/service

### Metrics (Future)
- Request latency
- Error rates
- Model inference time
- Memory usage
- API usage by endpoint

## Technology Choices

### Why FastAPI?
- Fast performance (ASGI)
- Automatic OpenAPI docs
- Pydantic integration
- Modern Python async support
- Easy to learn and use

### Why React?
- Component-based architecture
- Large ecosystem
- Fast rendering
- Good developer experience
- Vite for fast builds

### Why In-Memory Caching?
- Processed data is static
- Total size is small (~1.5 MB)
- Eliminates database complexity
- Very fast access (<1ms)
- Sufficient for hackathon/demo

### Why CSV Storage?
- Simple and portable
- Human-readable
- Easy to inspect and debug
- No database setup required
- Pandas integration

## Dependencies

### Backend
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `scikit-learn`: ML algorithms
- `xgboost`: Gradient boosting
- `joblib`: Model serialization
- `pydantic`: Data validation

### Frontend
- `react`: UI framework
- `react-dom`: DOM rendering
- `vite`: Build tool
- `tailwindcss`: Styling
- `plotly.js`: Charting
- `react-plotly.js`: React wrapper
- `axios`: HTTP client

## File Organization

```
carbon-market-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app & CORS
│   │   ├── api/             # Endpoint routers
│   │   │   ├── health.py
│   │   │   ├── market.py
│   │   │   ├── countries.py
│   │   │   ├── trading.py
│   │   │   └── scenario.py
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       └── data_service.py  # Data loading
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── App.jsx          # Root component
│   │   └── main.jsx         # Entry point
│   ├── index.html           # HTML template
│   ├── vite.config.js       # Vite config
│   └── package.json         # Dependencies
├── ml/
│   ├── training/            # Training scripts
│   ├── models/              # Saved models
│   ├── scenario_simulator.py
│   └── paths.py             # Path utilities
├── data/
│   ├── raw/                 # Original data
│   └── processed/           # ML-ready data
├── docs/                    # Documentation
├── requirements.txt         # Python deps
└── README.md                # Project overview
```
