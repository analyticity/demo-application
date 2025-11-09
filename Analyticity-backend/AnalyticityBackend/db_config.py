import os
import logging
import psycopg2
from psycopg2 import OperationalError
from fastapi import HTTPException

# Load .env if present (works locally and in Docker)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

logger = logging.getLogger("app.db")

# Single DB config: BRNO only
DATABASES = {
    "brno": {
        # Prefer DB_BRNO_* if provided; fall back to your root .env names
        "host": os.getenv("DB_BRNO_HOST", os.getenv("DB_HOST", "brno-db")),
        "port": os.getenv("DB_BRNO_PORT", os.getenv("DB_PORT", "5432")),
        "user": os.getenv("DB_BRNO_USER", os.getenv("POSTGRES_USER_BRNO", "analyticity_admin")),
        "password": os.getenv("DB_BRNO_PASSWORD", os.getenv("POSTGRES_PASSWORD_BRNO", "admin")),
        "dbname": os.getenv("DB_BRNO_NAME", os.getenv("POSTGRES_DB_BRNO", "traffic_brno")),
    }
}

def get_db_connection(db_name: str = "brno"):
    db = DATABASES.get(db_name)
    if not db:
        logger.warning("Database '%s' not found in config", db_name)
        raise HTTPException(status_code=404, detail="Database not found")

    safe_dsn = f"postgresql://{db['user']}@{db['host']}:{db['port']}/{db['dbname']}"
    try:
        logger.debug("Attempting DB connection: %s", safe_dsn)
        conn = psycopg2.connect(
            host=db["host"],
            port=db["port"],
            user=db["user"],
            password=db["password"],
            dbname=db["dbname"],
            connect_timeout=5
        )
        logger.info("✅ Connected to DB '%s' at %s", db_name, safe_dsn)
        return conn

    except OperationalError as e:
        logger.exception("❌ OperationalError connecting to %s: %s", safe_dsn, e)
        raise HTTPException(status_code=503, detail=f"Database '{db_name}' unavailable")
    except psycopg2.Error as e:
        logger.exception("❌ psycopg2 error connecting to %s: %s", safe_dsn, e)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        logger.exception("❌ Unexpected error connecting to %s: %s", safe_dsn, e)
        raise HTTPException(status_code=500, detail="Unexpected DB connection error")
