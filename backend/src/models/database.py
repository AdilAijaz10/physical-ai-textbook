from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config.settings import settings
import re


# For Neon Postgres
DATABASE_URL = settings.database_url.strip()

# Validate DATABASE_URL format
if DATABASE_URL.startswith('http://') or DATABASE_URL.startswith('https://'):
    raise ValueError(
        f"\n{'='*70}\n"
        f"ERROR: Invalid DATABASE_URL format detected!\n"
        f"{'='*70}\n"
        f"Your DATABASE_URL starts with '{DATABASE_URL[:8]}...' which is incorrect.\n\n"
        f"To fix this:\n"
        f"1. Go to your Neon dashboard (https://console.neon.tech/)\n"
        f"2. Select your project and database\n"
        f"3. Click on 'Connection Details' or 'Connection String'\n"
        f"4. Copy the connection string that starts with 'postgresql://'\n"
        f"5. Update DATABASE_URL in backend/.env file\n\n"
        f"Correct format should look like:\n"
        f"  postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require\n\n"
        f"Or for async connections:\n"
        f"  postgresql+asyncpg://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require\n"
        f"{'='*70}\n"
    )

# Check for common mistakes
if '/rest/v1' in DATABASE_URL or '.apirest.' in DATABASE_URL:
    raise ValueError(
        f"\n{'='*70}\n"
        f"ERROR: You're using a REST API endpoint, not a PostgreSQL connection string!\n"
        f"{'='*70}\n"
        f"Your DATABASE_URL appears to be: {DATABASE_URL[:80]}...\n\n"
        f"This looks like a REST API endpoint (notice '/rest/v1' or '.apirest.').\n"
        f"You need the PostgreSQL connection string instead!\n\n"
        f"To fix this:\n"
        f"1. Go to your Neon dashboard: https://console.neon.tech/\n"
        f"2. Select your project → Select your database\n"
        f"3. Click on 'Connection Details' or 'Connection String'\n"
        f"4. Look for the section labeled 'Connection string' or 'Postgres'\n"
        f"5. Copy the string that starts with 'postgresql://'\n"
        f"6. It should include your username and password\n"
        f"7. Update DATABASE_URL in backend/.env file (remove any spaces after =)\n\n"
        f"Correct format example:\n"
        f"  DATABASE_URL=postgresql://username:password@ep-aged-silence-ah8qksx7.us-east-1.aws.neon.tech/neondb?sslmode=require\n\n"
        f"Note: Remove the space after '=' and use 'postgresql://' not the REST API URL\n"
        f"{'='*70}\n"
    )

if not DATABASE_URL.startswith(('postgresql://', 'postgresql+asyncpg://', 'postgres://')):
    raise ValueError(
        f"\n{'='*70}\n"
        f"ERROR: Invalid DATABASE_URL format!\n"
        f"{'='*70}\n"
        f"Expected a PostgreSQL connection string starting with 'postgresql://' or 'postgresql+asyncpg://'\n"
        f"But got: {DATABASE_URL[:80]}...\n\n"
        f"To fix this:\n"
        f"1. Go to your Neon dashboard: https://console.neon.tech/\n"
        f"2. Select your project → Select your database\n"
        f"3. Click on 'Connection Details' or 'Connection String'\n"
        f"4. Copy the connection string that starts with 'postgresql://'\n"
        f"5. Update DATABASE_URL in backend/.env file\n"
        f"6. Make sure there's NO space after the '=' sign\n\n"
        f"Correct format:\n"
        f"  DATABASE_URL=postgresql://username:password@host/dbname?sslmode=require\n"
        f"{'='*70}\n"
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()