import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from fastapi import APIRouter, HTTPException, Request
from psycopg2.extras import RealDictCursor

from db_config import get_db_connection
from models.request_models import PlotDataRequestBody
from helpers.logging_helpers import request_extras, Stopwatch, safe_dsn_from_connection
from constants.queries import (
    QUERY_ALERTS_TYPES_BASE,
    QUERY_ALERTS_TYPES_WITH_STREETS,
    QUERY_TOP_STREETS_JAMS_BASE,
    QUERY_TOP_STREETS_JAMS_WITH_STREETS,
    QUERY_TOP_STREETS_ALERTS_BASE,
    QUERY_TOP_STREETS_ALERTS_WITH_STREETS,
)

router = APIRouter(tags=["dashboard"])
logger = logging.getLogger("app.dashboard")


def _fetch_alerts_type_rows(
    cursor,
    from_date: datetime,
    to_date: datetime,
    streets: Optional[List[str]],
) -> List[Dict[str, Any]]:
    """Run SQL and return rows: [{type, subtype, count}, ...]."""
    streets = streets or []

    if streets:
        if not all(isinstance(s, str) and s.strip() for s in streets):
            raise HTTPException(status_code=400, detail="Invalid 'streets' list.")
        cursor.execute(QUERY_ALERTS_TYPES_WITH_STREETS, (from_date, to_date, streets))
    else:
        cursor.execute(QUERY_ALERTS_TYPES_BASE, (from_date, to_date))

    return cursor.fetchall()


def _aggregate_alerts_types(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Transform flat rows into:
    {
      "basic_types_values": [...],         # counts per type (desc)
      "basic_types_labels": [...],         # type names in the same order,
      "<type>": {                          # for each type:
        "subtype_values": [...],           #   subtype counts (desc within type)
        "subtype_labels": [...],           #   subtype names
      },
      ...
    }
    """
    # Sum by type + subtype (defensive in case the backend or partitions return duplicated keys)
    by_type: Dict[str, Dict[str, int]] = {}
    for r in rows:
        t = (r.get("type") or "NOT_DEFINED").strip() or "NOT_DEFINED"
        st = (r.get("subtype") or "NOT_DEFINED").strip() or "NOT_DEFINED"
        cnt = int(r.get("count") or 0)
        by_type.setdefault(t, {})
        by_type[t][st] = by_type[t].get(st, 0) + cnt

    # Totals per type
    type_totals = [(t, sum(sub.values())) for t, sub in by_type.items()]
    type_totals.sort(key=lambda x: x[1], reverse=True)

    basic_types_labels = [t for t, _ in type_totals]
    basic_types_values = [c for _, c in type_totals]

    result: Dict[str, Any] = {
        "basic_types_values": basic_types_values,
        "basic_types_labels": basic_types_labels,
    }

    # Per-type subtype arrays (desc by count)
    for t, _ in type_totals:
        sub_items = sorted(by_type[t].items(), key=lambda x: x[1], reverse=True)
        result[t] = {
            "subtype_values": [cnt for _, cnt in sub_items],
            "subtype_labels": [name for name, _ in sub_items],
        }

    return result


@router.post("/{name}/data_for_plot_alerts/")
async def get_data_for_plot_pies(name: str, body: PlotDataRequestBody, request: Request) -> Dict[str, Any]:
    """
    Returns counts of alert types and subtypes over the given time interval.
    - Filters: time interval [from_date, to_date] (YYYY-MM-DD); optional streets (list of strings).
    - Route filtering is intentionally disabled.
    - Output shape:
      {
        "basic_types_values": [...],
        "basic_types_labels": [...],
        "<type>": { "subtype_values": [...], "subtype_labels": [...] },
        ...
      }
    """
    extras = request_extras(request)
    connection: Optional[psycopg2.extensions.connection] = None
    cursor: Optional[psycopg2.extensions.cursor] = None
    whole = Stopwatch()

    # 1) Validate dates (+ include whole 'to' day)
    try:
        from_date = datetime.strptime(body.from_date, "%Y-%m-%d")
        to_date = datetime.strptime(body.to_date, "%Y-%m-%d") + timedelta(days=1)
    except Exception:
        logger.warning("[plot_alerts_types] Invalid date format. Expected YYYY-MM-DD.", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    if from_date >= to_date:
        logger.warning(f"[plot_alerts_types] Invalid date range: {from_date}..{to_date}", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="'from_date' must be before 'to_date'.")

    streets = body.streets or []
    if body.route:
        logger.info("[plot_alerts_types] Route filter ignored (disabled by config).", extra=extras)

    logger.info(
        f"[plot_alerts_types] range={from_date.date()}..{(to_date - timedelta(days=1)).date()} streets={len(streets)}",
        extra=extras,
    )

    # 2) DB query
    try:
        connection = get_db_connection(name)
        logger.info(f"[plot_alerts_types] DB connection established: {safe_dsn_from_connection(connection)}", extra=extras)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        qsw = Stopwatch()
        rows = _fetch_alerts_type_rows(cursor, from_date, to_date, streets)
        logger.info(f"[plot_alerts_types] Rows fetched: {len(rows)}", extra=extras | {"duration_ms": qsw.ms()})

        if not rows:
            logger.warning("[plot_alerts_types] No alerts found for selected parameters.", extra=extras | {"status": 404})
            raise HTTPException(status_code=404, detail="No alerts found for the selected parameters.")

        # 3) Aggregate to expected shape
        asw = Stopwatch()
        result = _aggregate_alerts_types(rows)
        logger.info(
            f"[plot_alerts_types] Aggregation completed; distinct_types={len(result.get('basic_types_labels', []))}",
            extra=extras | {"duration_ms": asw.ms()},
        )
        return result

    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        logger.exception(f"[plot_alerts_types] OperationalError: {e}", extra=extras | {"status": 503})
        raise HTTPException(status_code=503, detail="Database unavailable")
    except psycopg2.Error as e:
        logger.exception(f"[plot_alerts_types] psycopg2 error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Query execution error")
    except Exception as e:
        logger.exception(f"[plot_alerts_types] Unexpected error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            logger.exception("[plot_alerts_types] Failed to close cursor", extra=extras)
        try:
            if connection is not None:
                connection.close()
                logger.info(
                    f"[plot_alerts_types] DB connection closed; total handler time {whole.ms()} ms",
                    extra=extras | {"duration_ms": whole.ms()},
                )
        except Exception:
            logger.exception("[plot_alerts_types] Failed to close connection", extra=extras)

def _fetch_top_streets(
    cursor,
    from_date: datetime,
    to_date: datetime,
    streets: Optional[List[str]],
    limit_n: int,
    *,
    which: str,  # "jams" | "alerts"
) -> Tuple[List[str], List[int]]:
    """Run the appropriate SQL and return (streets, counts) for the chosen source."""
    streets = streets or []
    params: Tuple[Any, ...]
    rows: List[Dict[str, Any]]

    if which == "jams":
        if streets:
            params = (from_date, to_date, streets, limit_n)
            cursor.execute(QUERY_TOP_STREETS_JAMS_WITH_STREETS, params)
        else:
            params = (from_date, to_date, limit_n)
            cursor.execute(QUERY_TOP_STREETS_JAMS_BASE, params)
    elif which == "alerts":
        if streets:
            params = (from_date, to_date, streets, limit_n)
            cursor.execute(QUERY_TOP_STREETS_ALERTS_WITH_STREETS, params)
        else:
            params = (from_date, to_date, limit_n)
            cursor.execute(QUERY_TOP_STREETS_ALERTS_BASE, params)
    else:
        raise ValueError("Invalid 'which' argument")

    rows = cursor.fetchall() or []
    streets_out = [r["street"] for r in rows]
    counts_out = [int(r["cnt"]) for r in rows]
    return streets_out, counts_out


@router.post("/{name}/data_for_plot_streets/")
async def get_data_for_plot_bar(name: str, body: PlotDataRequestBody, request: Request) -> Dict[str, Any]:
    """
    Returns data needed for bar charts (critical streets) from the DB (no get_data).
    - Time interval: [from_date, to_date] (YYYY-MM-DD; 'to' inclusive).
    - Optional `streets` list narrows the ranking to those streets only.
    - `route` filtering is currently ignored; logged for transparency.
    """
    extras = request_extras(request)
    connection: Optional[psycopg2.extensions.connection] = None
    cursor: Optional[psycopg2.extensions.cursor] = None
    whole = Stopwatch()

    # 1) Parse & validate dates
    try:
        from_date = datetime.strptime(body.from_date, "%Y-%m-%d")
        to_date = datetime.strptime(body.to_date, "%Y-%m-%d") + timedelta(days=1)  # include full 'to' day
    except Exception:
        logger.warning("[plot_streets] Invalid date format. Expected YYYY-MM-DD.", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    if from_date >= to_date:
        logger.warning(f"[plot_streets] Invalid date range: {from_date}..{to_date}", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="'from_date' must be before 'to_date'.")

    streets_filter = body.streets or []
    if body.route:
        # As requested earlier for alerts: route filtering is off. We keep consistent behavior here.
        logger.info("[plot_streets] Route filter ignored (disabled).", extra=extras)

    logger.info(
        f"[plot_streets] range={from_date.date()}..{(to_date - timedelta(days=1)).date()} streets_filter={len(streets_filter)}",
        extra=extras,
    )

    # 2) DB + queries
    try:
        connection = get_db_connection(name)
        logger.info(f"[plot_streets] DB connection established: {safe_dsn_from_connection(connection)}", extra=extras)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # top-N jams streets
        sw_j = Stopwatch()
        streets_jams, values_jams = _fetch_top_streets(cursor, from_date, to_date, streets_filter, limit_n=10, which="jams")
        logger.info(
            f"[plot_streets] JAMS top streets fetched; n={len(streets_jams)}",
            extra=extras | {"duration_ms": sw_j.ms()},
        )

        # top-N alerts streets
        sw_a = Stopwatch()
        streets_alerts, values_alerts = _fetch_top_streets(cursor, from_date, to_date, streets_filter, limit_n=10, which="alerts")
        logger.info(
            f"[plot_streets] ALERTS top streets fetched; n={len(streets_alerts)}",
            extra=extras | {"duration_ms": sw_a.ms()},
        )

        # if both empty -> 404
        if not streets_jams and not streets_alerts:
            logger.warning("[plot_streets] No data found for selected parameters.", extra=extras | {"status": 404})
            raise HTTPException(status_code=404, detail="No data found for the selected parameters.")

        payload = {
            "streets_jams": streets_jams,
            "values_jams": values_jams,
            "streets_alerts": streets_alerts,
            "values_alerts": values_alerts,
        }
        return payload

    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        logger.exception(f"[plot_streets] OperationalError: {e}", extra=extras | {"status": 503})
        raise HTTPException(status_code=503, detail="Database unavailable")
    except psycopg2.Error as e:
        logger.exception(f"[plot_streets] psycopg2 error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Query execution error")
    except Exception as e:
        logger.exception(f"[plot_streets] Unexpected error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            logger.exception("[plot_streets] Failed to close cursor", extra=extras)
        try:
            if connection is not None:
                connection.close()
                logger.info(
                    f"[plot_streets] DB connection closed; total handler time {whole.ms()} ms",
                    extra=extras | {"duration_ms": whole.ms()},
                )
        except Exception:
            logger.exception("[plot_streets] Failed to close connection", extra=extras)
