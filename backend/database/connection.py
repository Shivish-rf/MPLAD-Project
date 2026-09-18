import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Use pathlib to cleanly resolve the base directory (3 levels up)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. Pathlib allows you to use the '/' operator for joining paths
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
load_dotenv(ENV_PATH)

# Read database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Stop immediately if DATABASE_URL is missing
if not DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL was not found.\n"
        f"Expected .env file at:\n{ENV_PATH}"
    )

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3. Use the modern SQLAlchemy 2.0 class-based syntax for the Base model
class Base(DeclarativeBase):
    pass