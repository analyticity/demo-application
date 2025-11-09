# import logging
# import psycopg2
# from datetime import datetime, timedelta
# from typing import Optional, List
#
# from fastapi import APIRouter, HTTPException, Request
# from psycopg2.extras import RealDictCursor
#
# from constants.queries import (
#     QUERY_ALERTS_WITH_ROUTE,
#     QUERY_ALERTS_WITH_STREETS,
#     QUERY_ALERTS,
# )
# from db_config import get_db_connection
# from models.request_models import PlotDataRequestBody
#
# router = APIRouter(tags=["alerts"])
# logger = logging.getLogger("app.alerts")
#
#
# def _build_linestring(route: List[List[float]]) -> str:
#     """
#     Convert [[lon, lat], ...] into WKT LINESTRING(lon lat, lon lat, ...).
#     - Validates each coordinate to avoid malformed SQL parameters.
#     - NOTE: We pass this as a parameter to cursor.execute to avoid SQL injection.
#     """
#     parts = []
#     for idx, pair in enumerate(route):
#         try:
#             lon, lat = float(pair[0]), float(pair[1])
#         except Exception:
#             raise HTTPException(status_code=400, detail=f"Invalid route coordinate at index {idx}")
#         parts.append(f"{lon} {lat}")
#     return "LINESTRING(" + ", ".join(parts) + ")"
#
#
# @router.post("/{name}/draw_alerts/")
# async def get_all_alerts_for_drawing(name: str, body: PlotDataRequestBody, request: Request):
#     """
#     Return Waze alerts for drawing based on:
#       - time interval [from_date, to_date]
#       - optional list of streets OR a concrete route (polyline).
#
#     Logging:
#       - logs input parsing, query selection, timings and row counts
#       - avoids logging sensitive data or overly large payloads
#     """
#     request_id = getattr(request.state, "request_id", "unknown")
#     connection: Optional[psycopg2.extensions.connection] = None
#     cursor: Optional[psycopg2.extensions.cursor] = None
#
#     # Parse dates with validation
#     try:
#         from_date = datetime.strptime(body.from_date, "%Y-%m-%d")
#         # Include the entire 'to' day by adding one day and using '< next day' semantics in SQL
#         to_date = datetime.strptime(body.to_date, "%Y-%m-%d") + timedelta(days=1)
#     except Exception:
#         logger.warning(
#             "[draw_alerts] Invalid date format. Expected YYYY-MM-DD.",
#             extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
#         )
#         raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
#
#     streets = body.streets or []
#     route = body.route or []
#
#     # Reject mixed filters (both streets and route) if your logic expects XOR
#     if streets and route:
#         logger.warning(
#             "[draw_alerts] Both 'streets' and 'route' provided; expected only one.",
#             extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
#         )
#         raise HTTPException(status_code=400, detail="Provide either 'streets' or 'route', not both.")
#
#     # Log input summary (do not dump large arrays)
#     logger.info(
#         "[draw_alerts] Input parsed",
#         extra={
#             "request_id": request_id,
#             "path": request.url.path,
#             "method": "POST",
#             "from": body.from_date,
#             "to": body.to_date,
#             "streets_count": len(streets),
#             "route_points": len(route),
#         },
#     )
#
#     try:
#         # Establish DB connection
#         connection = get_db_connection(name)
#         cursor = connection.cursor(cursor_factory=RealDictCursor)
#
#         # Choose query and parameters
#         if not streets and not route:
#             query = QUERY_ALERTS
#             params = (from_date, to_date)
#             qlabel = "ALL"
#         elif streets and not route:
#             # Ensure streets is a list of strings
#             if not all(isinstance(s, str) and s.strip() for s in streets):
#                 raise HTTPException(status_code=400, detail="Invalid 'streets' list.")
#             query = QUERY_ALERTS_WITH_STREETS
#             params = (from_date, to_date, streets)
#             qlabel = f"STREETS[{len(streets)}]"
#         else:
#             # route only
#             if not isinstance(route, list) or len(route) < 2:
#                 raise HTTPException(status_code=400, detail="Route must contain at least two points.")
#             linestring = _build_linestring(route)
#             query = QUERY_ALERTS_WITH_ROUTE
#             params = (from_date, to_date, linestring)
#             qlabel = f"ROUTE[{len(route)}]"
#
#         # Execute query with timing
#         t0 = datetime.now()
#         cursor.execute(query, params)
#         rows = cursor.fetchall()
#         elapsed_ms = int((datetime.now() - t0).total_seconds() * 1000)
#
#         logger.info(
#             f"[draw_alerts] Query {qlabel} executed in {elapsed_ms} ms; rows={len(rows)}",
#             extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
#         )
#
#         if not rows:
#             logger.warning(
#                 "[draw_alerts] No data found for the selected parameters.",
#                 extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 404},
#             )
#             raise HTTPException(status_code=404, detail="No data found for the selected parameters.")
#
#         return rows
#
#     except HTTPException:
#         # Already logged / meaningful status code
#         raise
#
#     except psycopg2.OperationalError as e:
#         logger.exception(
#             f"[draw_alerts] OperationalError: {e}",
#             extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 503},
#         )
#         raise HTTPException(status_code=503, detail="Database unavailable")
#
#     except psycopg2.Error as e:
#         logger.exception(
#             f"[draw_alerts] Database query error: {e}",
#             extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 500},
#         )
#         raise HTTPException(status_code=500, detail="Database query error")
#
#     except Exception as e:
#         logger.exception(
#             f"[draw_alerts] Unexpected error: {e}",
#             extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 500},
#         )
#         raise HTTPException(status_code=500, detail="Internal server error")
#
#     finally:
#         # Always close resources
#         try:
#             if cursor:
#                 cursor.close()
#         except Exception:
#             logger.exception(
#                 "[draw_alerts] Failed to close cursor",
#                 extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
#             )
#         try:
#             if connection:
#                 connection.close()
#         except Exception:
#             logger.exception(
#                 "[draw_alerts] Failed to close connection",
#                 extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
#             )

# app/routers/alerts_draw_endpoints.py
import logging
from datetime import datetime, timedelta
from typing import Optional, List

import psycopg2
from fastapi import APIRouter, HTTPException, Request
from psycopg2.extras import RealDictCursor

from constants.queries import (
    QUERY_ALERTS_WITH_ROUTE,
    QUERY_ALERTS_WITH_STREETS,
    QUERY_ALERTS,
)
from db_config import get_db_connection
from models.request_models import PlotDataRequestBody
from helpers.logging_helpers import request_extras, Stopwatch  # <-- helpery na logovanie/časovanie

router = APIRouter(tags=["alerts"])
logger = logging.getLogger("app.alerts")


def _build_linestring(route: List[List[float]]) -> str:
    """
    Convert [[lon, lat], ...] -> WKT LINESTRING(lon lat, lon lat, ...).
    Validácia čísel a dĺžky. Samotný WKT posielame ako parameter do execute().
    """
    if not isinstance(route, list) or len(route) < 2:
        raise HTTPException(status_code=400, detail="Route must contain at least two points.")

    parts: List[str] = []
    for idx, pair in enumerate(route):
        try:
            lon, lat = float(pair[0]), float(pair[1])
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid route coordinate at index {idx}")
        parts.append(f"{lon} {lat}")
    return "LINESTRING(" + ", ".join(parts) + ")"


@router.post("/{name}/draw_alerts/")
async def get_all_alerts_for_drawing(name: str, body: PlotDataRequestBody, request: Request):
    """
    Vráti Waze alerts pre vykreslenie podľa:
      - intervalu [from_date, to_date]
      - voliteľne zoznamu ulíc ALEBO konkrétnej trasy (polyline)
    """
    extras = request_extras(request)
    connection: Optional[psycopg2.extensions.connection] = None
    cursor: Optional[psycopg2.extensions.cursor] = None
    whole = Stopwatch()

    # --- 1) Parsovanie/validácia vstupov ---
    try:
        from_date = datetime.strptime(body.from_date, "%Y-%m-%d")
        to_date = datetime.strptime(body.to_date, "%Y-%m-%d") + timedelta(days=1) #whole day from toDate
    except Exception:
        logger.warning("[draw_alerts] Invalid date format. Expected YYYY-MM-DD.", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    streets = body.streets or []
    route = body.route or []

    if streets and route:
        logger.warning("[draw_alerts] Both 'streets' and 'route' provided; expected only one.", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="Provide either 'streets' or 'route', not both.")

    logger.info(
        f"[draw_alerts] Input parsed: range={from_date.date()}..{(to_date - timedelta(days=1)).date()} "
        f"streets={len(streets)} route_points={len(route)}",
        extra=extras
    )

    try:
        connection = get_db_connection(name)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        if not streets and not route:
            query = QUERY_ALERTS
            params = (from_date, to_date)
            qlabel = "ALL"
            logger.info("[draw_alerts] Branch: ALL", extra=extras)
        elif streets and not route:
            if not all(isinstance(s, str) and s.strip() for s in streets):
                raise HTTPException(status_code=400, detail="Invalid 'streets' list.")
            query = QUERY_ALERTS_WITH_STREETS
            params = (from_date, to_date, streets)
            qlabel = f"STREETS[{len(streets)}]"
            logger.info(f"[draw_alerts] Branch: STREETS count={len(streets)}", extra=extras)
        else:
            linestring = _build_linestring(route)
            query = QUERY_ALERTS_WITH_ROUTE
            params = (from_date, to_date, linestring)
            qlabel = f"ROUTE[{len(route)}]"
            logger.info(f"[draw_alerts] Branch: ROUTE points={len(route)}", extra=extras)

        qsw = Stopwatch()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        q_ms = qsw.ms()
        logger.info(f"[draw_alerts] Query {qlabel} executed in {q_ms} ms; rows={len(rows)}", extra=extras | {"duration_ms": q_ms})

        if not rows:
            logger.warning("[draw_alerts] No data found for the selected parameters.", extra=extras | {"status": 404})
            raise HTTPException(status_code=404, detail="No data found for the selected parameters.")

        return rows

    except HTTPException:
        raise

    except psycopg2.OperationalError as e:
        logger.exception(f"[draw_alerts] OperationalError: {e}", extra=extras | {"status": 503})
        raise HTTPException(status_code=503, detail="Database unavailable")

    except psycopg2.Error as e:
        logger.exception(f"[draw_alerts] Database query error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Database query error")

    except Exception as e:
        logger.exception(f"[draw_alerts] Unexpected error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            logger.exception("[draw_alerts] Failed to close cursor", extra=extras)
        try:
            if connection:
                connection.close()
                total_ms = whole.ms()
                logger.info(f"[draw_alerts] DB connection closed; total handler time {total_ms} ms", extra=extras | {"duration_ms": total_ms})
        except Exception:
            logger.exception("[draw_alerts] Failed to close connection", extra=extras)
