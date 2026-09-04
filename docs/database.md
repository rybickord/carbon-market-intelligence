# Database Integration Guide

## Overview

The Carbon Market Intelligence system uses **PostgreSQL** as its primary database, with SQLAlchemy as the ORM and Alembic for schema migrations. The system includes a **fallback mechanism** that uses CSV files when the database is unavailable, ensuring the application remains operational during development or when PostgreSQL is not accessible.

## Architecture

### Technology Stack

- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic 1.13+
- **Driver**: psycopg 3.1+
- **Fallback**: CSV files from `data/processed/`

### Database Schema

The database consists of 7 main tables:

#### 1. `market_data`
Stores global carbon market historical timeseries data.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| year | INTEGER | Year (unique) |
| market_value | FLOAT | Market value in millions USD |
| market_volume | FLOAT | Market volume in MtCO2 |
| global_co2 | FLOAT | Global CO2 emissions |
| renewable_electricity_share | FLOAT | Renewable electricity percentage |
| renewable_production | FLOAT | Renewable production |
| global_gdp_growth | FLOAT | Global GDP growth rate |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

**Indexes**: `id`, `year` (unique)

#### 2. `country_intelligence`
Stores country-level intelligence data by year.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| country | STRING(100) | Country name |
| iso | STRING(10) | ISO country code |
| year | INTEGER | Year |
| co2 | FLOAT | CO2 emissions |
| per_capita_co2 | FLOAT | Per capita CO2 |
| renewable_electricity_share | FLOAT | Renewable electricity percentage |
| renewable_production | FLOAT | Renewable production |
| gdp_growth | FLOAT | GDP growth rate |
| carbon_rate_2023 | FLOAT | Carbon price rate |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

**Constraints**: Unique constraint on (country, year)  
**Indexes**: `id`, `country`, `iso`, `year`, composite (country, year)

#### 3. `company_trading`
Stores company trading transactions dataset.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| company_id | STRING(20) | Company identifier |
| industry_type | STRING(50) | Industry type |
| date | DATETIME | Transaction date |
| energy_demand_mwh | FLOAT | Energy demand in MWh |
| fuel_type | STRING(50) | Fuel type |
| emission_produced_tco2 | FLOAT | Emissions produced |
| emission_allowance_tco2 | FLOAT | Emission allowance |
| carbon_price_usd_per_t | FLOAT | Carbon price |
| transaction_type | STRING(20) | Transaction type |
| credits_traded_tco2 | FLOAT | Credits traded |
| verification_status | STRING(20) | Verification status |
| compliance_cost_usd | FLOAT | Compliance cost |
| optimization_scenario | STRING(50) | Optimization scenario |
| carbon_cost_savings_usd | FLOAT | Carbon cost savings |
| target_trade_action | INTEGER | Target action (0=Sell, 1=Buy) |
| created_at | TIMESTAMP | Record creation timestamp |

**Indexes**: `id`, `company_id`, `date`, `industry_type`, composite (company_id, date)

#### 4. `country_scores`
Stores country risk and opportunity scores.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| country | STRING(100) | Country name |
| iso | STRING(10) | ISO country code |
| year | INTEGER | Year |
| risk_score | FLOAT | Risk score (0-100) |
| risk_category | STRING(20) | Risk category |
| comp_co2, comp_per_cap, etc. | FLOAT | Component scores |
| opportunity_score | FLOAT | Opportunity score (0-100) |
| opportunity_category | STRING(20) | Opportunity category |
| comp_renew_elec, etc. | FLOAT | Component scores |
| flag_* | STRING(10) | Imputation flags |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

**Constraints**: Unique constraint on (country, year)  
**Indexes**: `id`, `country`, `year`, `risk_score`, `opportunity_score`, composite (country, year)

#### 5. `forecast_results`
Stores global market forecast results (historical + predictions).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| year | INTEGER | Year (unique) |
| market_value | FLOAT | Market value forecast |
| market_volume | FLOAT | Market volume forecast |
| series | STRING(20) | 'historical' or 'forecast' |
| market_value_model | STRING(50) | Model used for value |
| market_volume_model | STRING(50) | Model used for volume |
| created_at | TIMESTAMP | Record creation timestamp |

**Indexes**: `id`, `year` (unique)

#### 6. `scenario_results`
Stores scenario simulation history.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| carbon_price_change_pct | FLOAT | Carbon price change % |
| emissions_change_pct | FLOAT | Emissions change % |
| renewable_share_change_pct | FLOAT | Renewable share change % |
| gdp_growth_change_pct | FLOAT | GDP growth change % |
| baseline_market_value | FLOAT | Baseline value |
| baseline_market_volume | FLOAT | Baseline volume |
| scenario_market_value | FLOAT | Scenario value |
| scenario_market_volume | FLOAT | Scenario volume |
| value_change | FLOAT | Absolute value change |
| value_change_pct | FLOAT | Percentage value change |
| volume_change | FLOAT | Absolute volume change |
| volume_change_pct | FLOAT | Percentage volume change |
| model_info | TEXT | Model metadata (JSON) |
| warnings | TEXT | Warnings (JSON) |
| created_at | TIMESTAMP | Record creation timestamp |

**Indexes**: `id`, `created_at`

#### 7. `prediction_requests`
Stores company trading prediction request history.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| industry_type | STRING(50) | Industry type |
| fuel_type | STRING(50) | Fuel type |
| verification_status | STRING(20) | Verification status |
| energy_demand_mwh | FLOAT | Energy demand |
| emission_produced_tco2 | FLOAT | Emissions produced |
| emission_allowance_tco2 | FLOAT | Emission allowance |
| carbon_price_usd_per_t | FLOAT | Carbon price |
| compliance_cost_usd | FLOAT | Compliance cost |
| predicted_action | STRING(10) | Predicted action |
| probability | FLOAT | Prediction probability |
| confidence | STRING(20) | Confidence level |
| model_used | STRING(50) | Model used |
| created_at | TIMESTAMP | Record creation timestamp |

**Indexes**: `id`, `created_at`

## Setup Instructions

### Prerequisites

- PostgreSQL 15 or higher
- Python 3.8+
- All Python dependencies from `requirements.txt`

### Option 1: Docker Compose (Recommended)

If you have Docker installed, this is the easiest setup:

```bash
# Start PostgreSQL container
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs postgres

# Stop container
docker-compose down

# Stop and remove data
docker-compose down -v
```

**Default Configuration**:
- Host: `localhost`
- Port: `5432`
- Database: `carbon_market`
- User: `carbon_user`
- Password: `carbon_pass`

### Option 2: Local PostgreSQL Installation

#### Windows

1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run installer and follow wizard
3. Remember the password you set for the `postgres` user
4. Add PostgreSQL bin directory to PATH: `C:\Program Files\PostgreSQL\15\bin`

#### macOS

```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Create Database

Once PostgreSQL is installed:

```bash
# Option 1: Using psql
psql -U postgres
CREATE DATABASE carbon_market;
CREATE USER carbon_user WITH PASSWORD 'carbon_pass';
GRANT ALL PRIVILEGES ON DATABASE carbon_market TO carbon_user;
\q

# Option 2: Using createdb
createdb -U postgres carbon_market
psql -U postgres -c "CREATE USER carbon_user WITH PASSWORD 'carbon_pass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE carbon_market TO carbon_user;"
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit .env file
DATABASE_URL=postgresql+psycopg://carbon_user:carbon_pass@localhost:5432/carbon_market
```

**Format**: `postgresql+psycopg://username:password@host:port/database`

**Examples**:
- Local: `postgresql+psycopg://carbon_user:carbon_pass@localhost:5432/carbon_market`
- Docker: `postgresql+psycopg://carbon_user:carbon_pass@localhost:5432/carbon_market`
- Remote: `postgresql+psycopg://user:pass@remote.host.com:5432/dbname`

### Loading Environment Variables

The application automatically loads `.env` using `python-dotenv`. No additional configuration needed.

## Database Migrations

### Using Alembic

```bash
# Check current migration version
alembic current

# Upgrade to latest schema
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history

# Create new migration (after model changes)
alembic revision --autogenerate -m "description"
```

### Manual Schema Creation

Alternatively, use the initialization script:

```bash
python backend/scripts/init_database.py
```

## Data Loading

### Seed Database from CSV Files

Load all processed CSV data into PostgreSQL:

```bash
python backend/scripts/seed_database.py
```

**Features**:
- Idempotent (safe to run multiple times)
- Skips duplicate records based on unique constraints
- Batch commits for large datasets
- Progress reporting
- Error handling with helpful messages

**Data Sources**:
- `data/processed/global_market_timeseries.csv` → `market_data`
- `data/processed/country_intelligence.csv` → `country_intelligence`
- `data/processed/company_trading_dataset.csv` → `company_trading`
- `data/processed/country_risk_scores.csv` + `country_opportunity_scores.csv` → `country_scores`
- `data/processed/global_market_forecast.csv` → `forecast_results`

## Repository Pattern

The application uses a **repository pattern** to abstract database access:

### Available Repositories

#### MarketRepository
```python
from backend.database.database import SessionLocal
from backend.repositories.market_repository import MarketRepository

db = SessionLocal()
repo = MarketRepository(db)

# Get timeseries
timeseries = repo.get_timeseries()

# Get latest
latest = repo.get_latest()

# Get by year
data_2024 = repo.get_by_year(2024)

# Get forecast
forecast = repo.get_forecast()

db.close()
```

#### CountryRepository
```python
from backend.repositories.country_repository import CountryRepository

db = SessionLocal()
repo = CountryRepository(db)

# Get all countries
countries = repo.get_all_countries()

# Get country intelligence
china_data = repo.get_country_intelligence(country="China")

# Get latest data for country
latest = repo.get_country_latest("China")

# Get country scores
scores = repo.get_country_score("China")

# Get rankings
risk_ranking = repo.get_risk_ranking(limit=10)
opp_ranking = repo.get_opportunity_ranking(limit=10)

# Check if country exists
exists = repo.country_exists("China")

db.close()
```

#### TradingRepository
```python
from backend.repositories.trading_repository import TradingRepository

db = SessionLocal()
repo = TradingRepository(db)

# Get transactions
transactions = repo.get_all_transactions(skip=0, limit=100)

# Get by company
company_txns = repo.get_by_company("C001")

# Save prediction
prediction = repo.save_prediction(
    industry_type="Energy",
    fuel_type="Renewable",
    # ... other fields
    predicted_action="Buy",
    probability=0.75,
    confidence="High",
    model_used="LogisticRegression"
)

# Get prediction stats
stats = repo.get_prediction_stats()

db.close()
```

#### ScenarioRepository
```python
from backend.repositories.scenario_repository import ScenarioRepository

db = SessionLocal()
repo = ScenarioRepository(db)

# Save scenario
scenario = repo.save_scenario(
    carbon_price_change_pct=20.0,
    # ... other parameters
    baseline_market_value=535.0,
    scenario_market_value=550.0,
    # ... results
    model_info={"value_model": "Naive_LastValue"},
    warnings=["Extrapolation warning"]
)

# Get recent scenarios
recent = repo.get_recent_scenarios(limit=10)

# Get by ID
scenario = repo.get_scenario_by_id(1)

db.close()
```

## Fallback Mechanism

The system includes automatic fallback to CSV files when PostgreSQL is unavailable:

```python
from backend.services.data_service_db import get_data_service_db

service = get_data_service_db()

# Check data source
source = service.get_data_source()  # Returns "database" or "csv"
is_db = service.is_database_available()  # Returns True/False

# API remains the same regardless of source
df = service.get_global_market_timeseries()
countries = service.get_unique_countries()
```

**How it works**:
1. On startup, attempts to connect to PostgreSQL
2. If successful, uses database for all queries
3. If connection fails, falls back to CSV files
4. Application continues to function normally

## Testing

### Database Tests

Run comprehensive database tests:

```bash
# Set DATABASE_URL first
export DATABASE_URL="postgresql+psycopg://carbon_user:carbon_pass@localhost:5432/carbon_market"

# Run tests
python test_database.py
```

**Tests Include**:
- Database connection
- Table existence
- Repository operations
- Data insertion
- Data retrieval
- Ranking queries
- Statistics queries

### Integration with Existing Tests

The existing test suite (`test_backend.py`) automatically uses the fallback mechanism, so tests pass whether PostgreSQL is available or not.

## Performance Considerations

### Indexes

All frequently queried columns have indexes:
- Primary keys (`id` columns)
- Foreign key relationships
- Frequently filtered columns (country, year, date)
- Sorting columns (risk_score, opportunity_score, created_at)

### Connection Pooling

SQLAlchemy connection pool configuration (in `database.py`):
- Pool size: 5 connections
- Max overflow: 10 additional connections
- Pre-ping: Verifies connections before use

### Query Optimization

- Repositories use selective column loading where appropriate
- Pagination implemented for large datasets
- Batch commits for bulk inserts (1000 records per batch)
- Joins optimized with proper indexes

## Production Deployment

### Environment Variables

Set securely in production:

```bash
# Use strong passwords
DATABASE_URL=postgresql+psycopg://prod_user:STRONG_PASSWORD@db.host.com:5432/carbon_market_prod

# Optional: Enable SQLAlchemy query logging for debugging
SQLALCHEMY_ECHO=false
```

### Database Hosting Options

- **AWS RDS**: PostgreSQL managed service
- **Google Cloud SQL**: PostgreSQL managed service
- **Azure Database**: PostgreSQL managed service
- **Heroku Postgres**: Easy PostgreSQL hosting
- **DigitalOcean Databases**: PostgreSQL clusters

### Backup Strategy

```bash
# Backup database
pg_dump -U carbon_user -h localhost carbon_market > backup.sql

# Restore database
psql -U carbon_user -h localhost carbon_market < backup.sql

# Automated backups (example cron job)
0 2 * * * pg_dump -U carbon_user carbon_market | gzip > /backups/carbon_$(date +\%Y\%m\%d).sql.gz
```

### SSL/TLS Connection

For production, use encrypted connections:

```bash
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db?sslmode=require
```

## Troubleshooting

### Connection Refused

```
Error: could not connect to server: Connection refused
```

**Solutions**:
1. Check if PostgreSQL is running: `pg_isready` or `docker-compose ps`
2. Verify port 5432 is not in use by another process
3. Check firewall settings

### Authentication Failed

```
Error: FATAL: password authentication failed for user
```

**Solutions**:
1. Verify DATABASE_URL credentials
2. Check PostgreSQL user exists: `psql -U postgres -c "\du"`
3. Verify database exists: `psql -U postgres -c "\l"`

### Permission Denied

```
Error: permission denied for table
```

**Solutions**:
```sql
GRANT ALL PRIVILEGES ON DATABASE carbon_market TO carbon_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO carbon_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO carbon_user;
```

### Migration Conflicts

```
Error: Target database is not up to date
```

**Solutions**:
```bash
# Check current version
alembic current

# View pending migrations
alembic history

# Upgrade to latest
alembic upgrade head
```

### CSV Fallback Activated Unexpectedly

If the application falls back to CSV when you expect database:

1. Check DATABASE_URL is set correctly
2. Verify PostgreSQL is running
3. Test connection: `psql $DATABASE_URL`
4. Check application logs for connection errors

## Summary

The PostgreSQL integration provides:

✅ **Scalable data storage** for growing datasets  
✅ **Efficient queries** with indexes and connection pooling  
✅ **Data persistence** for predictions and scenarios  
✅ **Production-ready** architecture  
✅ **Automatic fallback** to CSV for development  
✅ **Migration management** with Alembic  
✅ **Repository pattern** for clean code organization  

The existing ML models, frontend, and API remain completely unchanged. Database integration is transparent to the rest of the application.
