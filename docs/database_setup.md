# PostgreSQL Database Setup - Quick Start Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.8+ installed
- Project dependencies installed: `pip install -r requirements.txt`
- PostgreSQL 15+ installed OR Docker installed

## Quick Setup (5 Minutes)

### Step 1: Start PostgreSQL

#### Option A: Using Docker (Recommended)

```bash
# Start PostgreSQL container
docker-compose up -d

# Verify it's running
docker-compose ps
```

#### Option B: Using Local PostgreSQL

If you have PostgreSQL installed locally, create the database:

```bash
# Create database and user
psql -U postgres
```

```sql
CREATE DATABASE carbon_market;
CREATE USER carbon_user WITH PASSWORD 'carbon_pass';
GRANT ALL PRIVILEGES ON DATABASE carbon_market TO carbon_user;
\q
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# The default DATABASE_URL should work:
# DATABASE_URL=postgresql+psycopg://carbon_user:carbon_pass@localhost:5432/carbon_market
```

If you changed the database credentials, edit `.env` accordingly.

### Step 3: Run Migrations

```bash
# Create database schema
alembic upgrade head
```

### Step 4: Load Data

```bash
# Import CSV data into PostgreSQL
python backend/scripts/seed_database.py
```

Expected output:
```
============================================================
CARBON MARKET INTELLIGENCE - DATABASE SEEDING
============================================================

Testing database connection...
✓ Database connection successful

Creating database tables...
✓ Tables created

Seeding market_data...
✓ Market data: 20 added, 0 skipped

Seeding country_intelligence...
  Progress: 1000 records added...
  Progress: 2000 records added...
  ...
✓ Country intelligence: 7099 added, 0 skipped

Seeding company_trading...
  Progress: 1000 records added...
  Progress: 2000 records added...
  ...
✓ Company trading: 5000 added

Seeding country_scores...
✓ Country scores: 223 added, 0 skipped

Seeding forecast_results...
✓ Forecast results: 23 added, 0 skipped

============================================================
✓ DATABASE SEEDING COMPLETE
============================================================
```

### Step 5: Verify Setup

```bash
# Run database tests
export DATABASE_URL="postgresql+psycopg://carbon_user:carbon_pass@localhost:5432/carbon_market"
python test_database.py
```

Expected output:
```
============================================================
DATABASE TESTS
============================================================
Testing database connection...
  ✓ Database connection successful
Testing database tables...
  ✓ Table 'market_data' exists
  ✓ Table 'country_intelligence' exists
  ...
============================================================
✓ ALL DATABASE TESTS PASSED!
============================================================
```

### Step 6: Start Application

```bash
# Backend (with database)
python run_backend.py

# Frontend (in separate terminal)
cd frontend
npm run dev
```

The application will now use PostgreSQL for data access! 🎉

## Verifying Database Integration

### Check Data Source

When you start the backend, look for this message:

```
✓ Using PostgreSQL database for data access
```

If PostgreSQL is not available, you'll see:

```
⚠ Database not available, falling back to CSV files
```

### Test API Endpoints

```bash
# Test market data (should come from database)
curl http://localhost:8000/api/market/overview

# Test country data (should come from database)
curl http://localhost:8000/api/countries?limit=5
```

## Common Issues

### Issue: "psql: command not found"

**Solution**: PostgreSQL is not installed or not in PATH.

- Windows: Add `C:\Program Files\PostgreSQL\15\bin` to PATH
- macOS: `brew install postgresql@15`
- Linux: `sudo apt install postgresql`

### Issue: "docker: command not found"

**Solution**: Docker is not installed.

Download from https://www.docker.com/products/docker-desktop

### Issue: "Connection refused" when seeding

**Solutions**:
1. Check if PostgreSQL is running: `docker-compose ps` or `pg_isready`
2. Verify port 5432 is not blocked
3. Check DATABASE_URL is correct

### Issue: "Database does not exist"

**Solution**: Create the database first:

```bash
psql -U postgres -c "CREATE DATABASE carbon_market;"
```

### Issue: "Permission denied for schema public"

**Solution**: Grant permissions:

```sql
psql -U postgres carbon_market
GRANT ALL ON SCHEMA public TO carbon_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO carbon_user;
```

## Alternative: Development Without PostgreSQL

If you don't want to set up PostgreSQL right now, the application will automatically fall back to CSV files:

```bash
# Just start the backend - it will use CSV files
python run_backend.py

# Output:
# ⚠ Database not available, falling back to CSV files
# ✓ Using CSV files for data access
```

The application works identically, but data is read from `data/processed/*.csv` instead of PostgreSQL.

## Next Steps

Once the database is set up:

1. **Run existing tests**: `python run_tests.py` (should still pass)
2. **Test database**: `python test_database.py` (new database tests)
3. **Explore data**: Use `psql` or a GUI tool like pgAdmin
4. **Make predictions**: Trading predictions are now saved to database
5. **View history**: Scenario simulations are now persisted

## Database Management Commands

```bash
# Connect to database
psql -U carbon_user -d carbon_market

# List tables
\dt

# View table schema
\d market_data

# Count records
SELECT COUNT(*) FROM market_data;
SELECT COUNT(*) FROM country_intelligence;
SELECT COUNT(*) FROM company_trading;

# View recent predictions
SELECT * FROM prediction_requests ORDER BY created_at DESC LIMIT 5;

# View recent scenarios
SELECT * FROM scenario_results ORDER BY created_at DESC LIMIT 5;

# Exit
\q
```

## Resetting Database

If you need to start fresh:

```bash
# Using Docker
docker-compose down -v  # Removes data volume
docker-compose up -d
alembic upgrade head
python backend/scripts/seed_database.py

# Using local PostgreSQL
dropdb -U postgres carbon_market
createdb -U postgres carbon_market
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE carbon_market TO carbon_user;"
alembic upgrade head
python backend/scripts/seed_database.py
```

## Production Deployment

For production, update `.env` with your production database:

```bash
# Example AWS RDS
DATABASE_URL=postgresql+psycopg://username:password@mydb.xxxxx.us-east-1.rds.amazonaws.com:5432/carbon_market

# Example Heroku
DATABASE_URL=postgresql+psycopg://user:pass@ec2-xx-xx-xx-xx.compute-1.amazonaws.com:5432/dbname
```

Then run migrations and seeding on production:

```bash
# On production server
alembic upgrade head
python backend/scripts/seed_database.py
```

## Support

If you encounter issues not covered here:

1. Check `docs/database.md` for detailed documentation
2. View logs: `docker-compose logs postgres` (if using Docker)
3. Test connection: `psql $DATABASE_URL` or `python -c "from backend.database.database import SessionLocal; db = SessionLocal(); db.execute('SELECT 1'); print('✓ Connected')"`
4. Verify environment: `echo $DATABASE_URL`

---

**Summary**: In 5 steps (start PostgreSQL, configure .env, run migrations, seed data, verify), you have a fully functional PostgreSQL-backed Carbon Market Intelligence system! 🚀
