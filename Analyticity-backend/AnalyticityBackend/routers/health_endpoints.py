import logging, time, psycopg2
from typing import Dict
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection, DATABASES
from helpers.logging_helpers import request_extras, Stopwatch

router = APIRouter()
logger = logging.getLogger("app")

TABLES_TO_CHECK: Dict[str, str] = {
    "alerts": "SELECT MIN(published_at) AS first_record, MAX(published_at) AS last_record FROM alerts;",
    "jams": "SELECT MIN(published_at) AS first_record, MAX(published_at) AS last_record FROM jams;",
    "accidents": "SELECT MIN(p2a) AS first_record, MAX(p2a) AS last_record FROM nehody;",
}


@router.get("/health/db")
async def db_healthcheck(request: Request):
    extras = request_extras(request, status="")
    results = {}
    all_sw = Stopwatch()

    for db_name in DATABASES.keys():
        conn = None
        db_info = {"status": "ok", "tables": {}, "latency_ms": None}
        sw = Stopwatch()

        try:
            conn = get_db_connection(db_name)
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                _ = cur.fetchone()

            db_info["latency_ms"] = sw.ms()
            logger.info(f"[health] DB '{db_name}' connectivity OK", extra=extras | {"duration_ms": db_info["latency_ms"], "status": 200})

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for table, query in TABLES_TO_CHECK.items():
                    try:
                        cur.execute(query)
                        res = cur.fetchone() or {}
                        db_info["tables"][table] = {
                            "first_record": str(res.get("first_record")) if res.get("first_record") else None,
                            "last_record": str(res.get("last_record")) if res.get("last_record") else None,
                            "missing": False,
                        }
                    except psycopg2.errors.UndefinedTable:
                        conn.rollback()
                        db_info["tables"][table] = {"missing": True}
                        logger.warning(f"[health] Table '{table}' missing in DB '{db_name}'", extra=extras | {"status": 200})
                    except Exception as e:
                        conn.rollback()
                        db_info["tables"][table] = {"error": str(e)}
                        logger.exception(f"[health] Error querying table '{table}' in DB '{db_name}': {e}", extra=extras | {"status": 500})

        except Exception as e:
            db_info["status"] = "failed"
            db_info["error"] = str(e)
            logger.exception(f"[health] DB '{db_name}' failure: {e}", extra=extras | {"status": 503})
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                logger.exception(f"[health] Failed to close connection for DB '{db_name}'", extra=extras)

        results[db_name] = db_info

    overall_ok = all(db.get("status") == "ok" for db in results.values())
    total_ms = all_sw.ms()
    payload = {"status": "ok" if overall_ok else "degraded", "total_ms": total_ms, "databases": results}
    status_code = 200 if overall_ok else 503

    logger.info(f"[health] Overall DB health: {payload['status']}", extra=extras | {"status": status_code, "duration_ms": total_ms})
    return JSONResponse(status_code=status_code, content=payload)
