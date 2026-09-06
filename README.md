# Carbon Market Intelligence

> AI-powered platform for analyzing, forecasting, and simulating the global voluntary carbon credit market.

---

## 🌐 Live Links

| | URL |
|---|---|
| **Live Demo** | [https://carbon-market-intelligence.vercel.app](https://carbon-market-intelligence.vercel.app) |
| **Backend API** | [https://carbon-market-intelligence.onrender.com](https://carbon-market-intelligence.onrender.com) |
| **API Docs** | [https://carbon-market-intelligence.onrender.com/docs](https://carbon-market-intelligence.onrender.com/docs) |

---

## Platform Modules

| Module | Description |
|---|---|
| **Overview** | Market KPIs, historical value & volume trends (2005–2024) |
| **Market Intelligence** | Key market drivers — policy, economics, renewables, corporate commitments |
| **Forecast** | ML-powered 1-year forward predictions for market value and volume |
| **Countries** | Risk and opportunity scoring for 223 countries |
| **Scenario Lab** | Interactive what-if analysis — adjust macro parameters and see model responses |
| **Trading** | Buy/Sell prediction for company carbon credits based on emissions profile |
| **Documentation** | Platform guide, API reference, and technical architecture |

---

## Tech Stack

### Frontend
- **React 18** + **Vite**
- **Tailwind CSS** — glassmorphism design system, mobile-responsive
- **Plotly.js** — interactive data visualizations
- **Axios** — API communication

### Backend
- **FastAPI** + **Pydantic** — high-performance REST API
- **PostgreSQL / Neon** — cloud-hosted relational database
- **SQLAlchemy** — ORM with repository pattern
- **uvicorn** — ASGI server

### Machine Learning & Data
- **Pandas**, **NumPy** — data processing
- **Scikit-learn** — Logistic Regression, preprocessing, walk-forward validation
- **XGBoost** — gradient boosting for market volume forecasting

---

## ML Models

### Global Market Forecasting

| Target | Model | RMSE | Notes |
|---|---|---|---|
| **Market Value** | Naive Last Value | 807.78 | Outperforms ML on this dataset due to structural breaks; repeats the latest known value as the baseline forecast |
| **Market Volume** | XGBoost | 172.25 | Trained on lagged market + macro features; responds to scenario inputs |

- **Validation**: Expanding-window walk-forward cross-validation
- **Features**: Lagged market values, CO₂ emissions, renewable energy share, GDP growth

### Company Trading Classifier

| Model | Accuracy | F1 Score | ROC-AUC |
|---|---|---|---|
| **Logistic Regression** | 0.517 | 0.542 | 0.517 |

- **Task**: Predict Buy or Sell based on company emissions profile
- **Features**: Industry type, fuel type, verification status, emissions produced vs. allowance, carbon price, compliance cost
- **Validation**: Stratified 80/20 train/test split

### Country Risk & Opportunity Scoring
- **Risk factors**: High per-capita CO₂, low renewable share, weak carbon pricing, regulatory exposure
- **Opportunity factors**: Renewable growth potential, GDP trajectory, carbon policy infrastructure
- **Scale**: 0–100 relative ranking across 223 countries

---

## Scenario Lab — How It Works & Limitations

The Scenario Lab lets you adjust four macro parameters and compare the resulting model prediction against the baseline:

| Parameter | Effect on Models |
|---|---|
| **Renewable Energy Share** | Feeds into Market Volume (XGBoost) |
| **GDP Growth** | Feeds into Market Volume (XGBoost) |
| **CO₂ Emissions** | Feeds into Market Volume (XGBoost) |
| **Carbon Price** | Not directly modeled in current forecasting; UI reflects this |

**Important constraints:**
- **Market Value always returns the Naive Last Value baseline** regardless of scenario inputs. This is intentional — the Naive model does not accept scenario parameters; it simply repeats the last known value.
- **Market Volume does respond** to Renewables, GDP, and CO₂ changes via the XGBoost model.
- **Carbon Price is not modeled** in the global forecasting pipeline. Changing it will not affect Market Value or Market Volume.
- Scenario changes are applied to lagged features, not contemporaneous values. The model captures historical relationships; it cannot predict structural regime changes.

---

## Data

- **Coverage**: 2005–2024 (20 annual observations)
- **Sources**:
  - Voluntary Carbon Market — historical market size by value and volume
  - Global Carbon Budget 2022 — country-level CO₂ emissions
  - Our World in Data / BP — renewable energy statistics (1965–2022)
  - World Bank — global GDP growth data
  - OECD — carbon pricing rates (2023)
  - Synthetic carbon trading transaction dataset (company-level)

> **Note:** All data is historical. The platform does not connect to real-time market feeds. Macro indicator data (CO₂, renewables) ends at 2021 and is forward-filled for 2022–2024. The latest available data is used throughout — this is not a live market data product.

---

## Project Structure

```
carbon-market-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── api/              # Route handlers
│   │   └── schemas.py        # Pydantic models
│   ├── database/             # SQLAlchemy config + models
│   ├── repositories/         # Repository pattern (market, country, trading, scenario)
│   ├── scripts/              # Database init & seed scripts
│   └── services/             # Data access layer (DB + CSV fallback)
├── frontend/
│   ├── src/
│   │   ├── components/       # React components + page sections
│   │   └── services/         # Axios API client
│   └── package.json
├── ml/
│   ├── training/             # Model training scripts
│   ├── models/               # Serialised trained models
│   └── scenario_simulator.py # Scenario computation logic
├── data/
│   ├── raw/                  # Source datasets
│   └── processed/            # ML-ready CSV outputs
├── docs/                     # Extended documentation
├── alembic/                  # Database migrations
├── docker-compose.yml        # Local PostgreSQL (optional)
├── .env.example              # Environment variable template
└── README.md
```

---

## Running Locally

### Prerequisites
- Python 3.8+
- Node.js 18+

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend (uses PostgreSQL/Neon or CSV fallback automatically)
python run_backend.py
```

API runs at `http://localhost:8000`  
Swagger UI at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

### Optional: Local PostgreSQL via Docker

```bash
docker-compose up -d
alembic upgrade head
python backend/scripts/seed_database.py
```

---

## API Reference

**Base URL (production):** `https://carbon-market-intelligence.onrender.com`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/market/overview` | Current market KPIs |
| GET | `/api/market/history` | Historical time series |
| GET | `/api/market/forecast` | ML forecast data |
| GET | `/api/market/metrics` | Model performance metrics |
| GET | `/api/countries` | All country data |
| GET | `/api/countries/risk` | Risk ranking |
| GET | `/api/countries/opportunity` | Opportunity ranking |
| POST | `/api/trading/predict` | Trading action prediction |
| GET | `/api/trading/model` | Trading model info |
| POST | `/api/scenario/simulate` | Scenario simulation |

Full interactive docs: [https://carbon-market-intelligence.onrender.com/docs](https://carbon-market-intelligence.onrender.com/docs)

---

## Known Limitations

| Area | Limitation |
|---|---|
| **Data volume** | Only 20 annual observations — small dataset for ML |
| **Market Value model** | Naive baseline; does not respond to scenario inputs |
| **Trading classifier** | F1 ≈ 0.54 — the task is genuinely difficult with available features |
| **Macro data lag** | CO₂ and renewables data ends 2021, forward-filled thereafter |
| **No real-time feeds** | All data is historical; prices and volumes are not live |
| **Scenario scope** | Cannot model structural market changes or policy discontinuities |
| **No uncertainty bands** | Point estimates only; no confidence intervals |

---

## License

Educational / demonstration project.

---

*Built for Smart India Hackathon (SIH) — Carbon Market Intelligence track.*
