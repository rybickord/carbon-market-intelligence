"""
Database initialization script.

Creates the database schema and optionally seeds with data.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    """Initialize database schema."""
    print("=" * 60)
    print("CARBON MARKET INTELLIGENCE - DATABASE INITIALIZATION")
    print("=" * 60)
    
    try:
        from backend.database.database import engine, SessionLocal
        from backend.database.models import Base
        
        # Test database connection
        print("\nTesting database connection...")
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✓ Database connection successful")
        
        # Create all tables
        print("\nCreating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
        
        print("\n" + "=" * 60)
        print("✓ DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run seed script: python backend/scripts/seed_database.py")
        print("2. Or use Alembic migrations: alembic upgrade head")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. DATABASE_URL environment variable is set correctly")
        print("3. Database exists and is accessible")
        print("\nExample DATABASE_URL:")
        print("  postgresql+psycopg://username:password@localhost:5432/carbon_market")
        print("\nYou can also create a .env file with DATABASE_URL")
        sys.exit(1)


if __name__ == "__main__":
    main()
