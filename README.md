# Carbon Market Intelligence & Prediction System

A comprehensive platform for analyzing, forecasting, and simulating global carbon credit markets using machine learning and data analytics.

## Overview

This hackathon project provides intelligence on the global carbon market through:
- **Historical Analysis**: 20 years of carbon market data (2005-2024)
- **ML-Powered Forecasting**: Predictions for market value and volume
- **Country Intelligence**: Risk and opportunity scoring for 223 countries
- **Trading Recommendations**: Buy/Sell predictions for company carbon credits
- **Scenario Simulation**: Interactive what-if analysis for market conditions

## Features

### 🌍 Global Market Analysis
- Real-time market overview with KPIs
- Historical trends and patterns (2005-2024)
- 3-year forward forecasts using validated ML models
- Walk-forward cross-validation for model selection

### 🗺️ Country Intelligence
- Risk scoring based on emissions, renewables, GDP, and carbon policy
- Opportunity scoring for market potential
- Detailed country profiles with latest data
- Interactive search and filtering

### 💼 Trading Prediction
- ML classifier for Buy/Sell recommendations
- Input validation preventing leakage
- Confidence levels and probability estimates
- Feature importance analysis

### 🎯 Scenario Simulator
- Interactive parameter adjustment (emissions, renewables, GDP, carbon price)
- Baseline vs scenario comparison
- Real-time predictions using Phase 3 models
- Warnings and interpretation guidance

## Architecture

### Data Pipeline
```
Raw Data Sources
    ↓
Data Processing (Phase 1-2)
    ↓
Processed Datasets (data/processed/)
    ↓
ML Training (Phase 3)
    ↓
Trained Models (ml/models/)
```

### Application Stack
```
Frontend (React + Vite + Tailwind + Plotly)
    ↓ HTTP/REST
Backend (FastAPI + Pydantic)
    ↓
ML Layer (scikit-learn + XGBoost)
    ↓
Data Layer (PostgreSQL + SQLAlchemy OR CSV fallback)
```

### Database Architecture

The system supports **PostgreSQL** as the primary database with automatic fallback to CSV files:

```
PostgreSQL (Production)
    ↓
SQLAlchemy ORM + Repository Pattern
    ↓
FastAPI Endpoints
    ↓
React Frontend

Fallback: CSV Files (Development)
```

**Features**:
- 7 database tables (market_data, country_intelligence, company_trading, country_scores, forecast_results, scenario_results, prediction_requests)
- Alembic migrations for schema management
- Repository pattern for clean data access
- Automatic fallback to CSV when database unavailable
- Docker Compose for easy PostgreSQL setup

See [`docs/database.md`](docs/database.md) for detailed database documentation.  
See [`docs/database_setup.md`](docs/database_setup.md) for quick setup guide.

## Project Structure

```
carbon-market-intelligence/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI application
│   │   ├── api/          # API endpoints
│   │   └── schemas.py    # Pydantic models
│   ├── database/         # Database layer
│   │   ├── database.py   # SQLAlchemy config
│   │   ├── models.py     # Database models
│   │   └── __init__.py
│   ├── repositories/     # Repository pattern
│   │   ├── market_repository.py
│   │   ├── country_repository.py
│   │   ├── trading_repository.py
│   │   └── scenario_repository.py
│   ├── scripts/          # Database scripts
│   │   ├── init_database.py
│   │   └── seed_database.py
│   └── services/
│       ├── data_service.py     # CSV data access
│       └── data_service_db.py  # Database + CSV fallback
├── frontend/             # React dashboard
│   ├── src/
│   │   ├── components/   # React components
│   │   └── services/     # API client
│   └── package.json
├── ml/                   # Machine learning
│   ├── training/         # Training scripts
│   ├── models/           # Trained models
│   ├── paths.py          # Path utilities
│   └── scenario_simulator.py
├── alembic/              # Database migrations
│   ├── versions/         # Migration scripts
│   └── env.py
├── data/
│   ├── raw/              # Original data (protected)
│   └── processed/        # ML-ready datasets
├── docs/                 # Documentation
│   ├── database.md       # Database guide
│   └── database_setup.md # Setup instructions
├── notebooks/            # Jupyter notebooks
├── docker-compose.yml    # PostgreSQL setup
├── .env.example          # Environment template
└── README.md

```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- pip/npm

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Option 1: With PostgreSQL (recommended)
# Start PostgreSQL via Docker
docker-compose up -d

# Run migrations
alembic upgrade head

# Seed database
python backend/scripts/seed_database.py

# Option 2: Without PostgreSQL (CSV fallback)
# Skip database steps, application will use CSV files

# Run tests
python run_tests.py

# Start backend server
python run_backend.py
```

Backend runs on `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on `http://localhost:3000`

## Usage

### Running the Complete Application

**Terminal 1 - Backend:**
```bash
python run_backend.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Browser:**
Open `http://localhost:3000`

### API Examples

**Get Market Overview:**
```bash
curl http://localhost:8000/api/market/overview
```

**Get Country Risk Ranking:**
```bash
curl http://localhost:8000/api/countries/risk?limit=10
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

## Data Sources

- **Voluntary Carbon Market**: Historical market size by value and volume
- **CO2 Emissions**: Global Carbon Budget 2022 (country-level emissions)
- **Renewable Energy**: World energy statistics (1965-2022)
- **GDP Growth**: World Bank global GDP data
- **Carbon Pricing**: OECD carbon rate database (2023)
- **Company Trading**: Synthetic carbon trading transaction dataset

## ML Models

### Global Market Forecasting
- **Market Value Model**: Naive_LastValue (RMSE: 807.78)
- **Market Volume Model**: XGBoost (RMSE: 172.25)
- **Validation**: Expanding-window walk-forward CV
- **Features**: Lagged market values, macro indicators (CO2, renewables, GDP)

### Company Trading Classifier
- **Model**: Logistic Regression
- **Accuracy**: 0.517 | **F1**: 0.5422 | **ROC-AUC**: 0.5168
- **Validation**: Stratified 80/20 train/test split
- **Features**: Industry, fuel type, emissions, allowance gap, carbon price

### Risk & Opportunity Scoring
- **Risk Components**: CO2 emissions, per-capita emissions, weak renewables, weak GDP, weak carbon policy
- **Opportunity Components**: Strong renewables, GDP growth, carbon policy, low baseline emissions
- **Scale**: 0-100 (relative ranking)

## Limitations

### Data Limitations
- Annual time series with only 20 observations (2005-2024)
- Macro indicators (CO2, renewables) end in 2021; forward-filled for 2022-2024
- Country data uses latest available year (2021)
- No real-time data feeds

### Model Limitations
- **Market Value**: Naive baseline outperforms ML (structural breaks in 2021)
- **Trading Classifier**: F1 score ~0.54 indicates difficult prediction task
- **Scenario Simulator**: Assumes historical patterns continue; cannot predict structural changes
- **No uncertainty quantification**: Point estimates without confidence intervals

### Technical Limitations
- Models trained on limited data
- No multi-year recursive forecasting
- Scenario changes applied to lagged features (not contemporaneous)
- Carbon price not directly modeled in global forecasts

## Testing

```bash
# Run all tests
python run_tests.py

# Run specific tests
python test_phase3_models.py
python test_backend.py
```

**Test Coverage:**
- Phase 3 model validation
- All 13 API endpoints
- Input validation
- Error handling

## Documentation

- **[Architecture](docs/architecture.md)**: System design and data flow
- **[API Documentation](docs/api.md)**: Complete API reference
- **[Testing](docs/testing.md)**: Test strategy and results
- **[Scenario Simulator](docs/scenario_simulator.md)**: Methodology and interpretation
- **[Demo Guide](docs/demo_guide.md)**: Presentation walkthrough
- **Phase 3 Results**:
  - [Global Market Forecasting](docs/global_market_forecasting.md)
  - [Company Trading Model](docs/company_trading_model.md)
  - [Risk Score Methodology](docs/risk_score_methodology.md)
  - [Opportunity Score Methodology](docs/opportunity_score_methodology.md)
  - [Phase 3 Results Summary](docs/phase3_results.md)

## Development

### Project Timeline
- **Phase 1-2**: Data collection and processing
- **Phase 3**: ML model training and validation ✓
- **Phase 4**: Scenario simulator and FastAPI backend ✓
- **Phase 5**: React frontend dashboard ✓
- **Phase 6**: Full integration ✓
- **Phase 7**: End-to-end testing ✓
- **Phase 8**: Documentation ✓
- **Phase 9**: Demo preparation ✓

### Tech Stack
- **Backend**: FastAPI, Pydantic, uvicorn
- **ML**: scikit-learn, XGBoost, pandas, numpy
- **Frontend**: React 18, Vite, Tailwind CSS, Plotly.js, Axios
- **Data**: CSV files, JSON metadata

## Future Enhancements

- Real-time data integration
- Multi-year recursive forecasting
- Uncertainty quantification (confidence intervals)
- Additional ML models (LSTM, Prophet)
- User authentication
- Data export functionality
- Mobile-responsive improvements
- Database backend (PostgreSQL/MongoDB)
- Deployment to cloud (AWS/Azure/GCP)

## License

Hackathon project - Educational use

## Contributors

Developed as part of a hackathon project for global carbon market intelligence.