
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# ---------------------------------------------------------
# LOAD .ENV FROM PROJECT ROOT
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)


# ---------------------------------------------------------
# DATABASE URL
# ---------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL was not found.\n"
        f"Expected .env file at:\n{ENV_PATH}"
    )


# ---------------------------------------------------------
# DATABASE ENGINE
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ---------------------------------------------------------
# BASE
# ---------------------------------------------------------

Base = declarative_base()

