from datetime import datetime, timedelta
from typing import List, Optional
import logging

import psycopg2
from fastapi import APIRouter, HTTPException, Request
from psycopg2.extras import RealDictCursor

from db_config import get_db_connection
from helpers.homepage_helpers import fetch_sum_statistics, fetch_hourly_by_streets, transform_to_response_statistics, \
    fetch_hourly_by_route, transform_to_response_statistics_v2, transform_sum_statistics_to_legacy_format, \
    fetch_total_statistics
from models.request_models import PlotDataRequestBody
from models.response_models import StatsResponse, LegacyPlotResponse, TotalStatsResponse
from helpers.logging_helpers import request_extras, Stopwatch, safe_dsn_from_connection


router = APIRouter(
    tags=["home"]
)
logger = logging.getLogger("app.homepage_endpoints")


#
# @router.post("/{name}/data_for_plot_drawer/")
# async def get_data_for_plot_drawer(name: str, body: PlotDataRequestBody):
#     """
#     Function returns basic statistics about traffic situation
#
#     :param name: Which area the data should be loaded
#     :param body: One object, containing data about time interval (from date, to date) and list of streets or concrete route
#     :return: Calculated statistics
#     """
#     connection = get_db_connection(name)
#
#     try:
#         cursor = connection.cursor(cursor_factory=RealDictCursor)
#
#         from_date = datetime.strptime(body.from_date, "%Y-%m-%d")
#         to_date = datetime.strptime(body.to_date, "%Y-%m-%d") + timedelta(days=1)  # to include entire day
#
#         streets = body.streets or []
#         route = body.route or []
#
#         if not streets and not route:
#             rows = fetch_sum_statistics(cursor, from_date, to_date)
#         if streets and not route:
#             rows = fetch_hourly_by_streets(cursor, from_date, to_date, streets)
#         if route:
#             rows = fetch_hourly_by_route(cursor, from_date, to_date, route)
#
#         if not rows:
#             raise HTTPException(status_code=404, detail="No data found for the selected parameters.")
#
#         response = transform_to_response_statistics(rows)
#         return response
#
#     except psycopg2.Error as e:
#         raise HTTPException(status_code=500, detail=f"Database query error: {e}")
#     finally:
#         if connection:
#             cursor.close()
#             connection.close()

@router.post("/{name}/data_for_plot_drawer/", response_model=LegacyPlotResponse)
async def get_data_for_plot_drawer_v2(name: str, body: PlotDataRequestBody, request: Request):
    """
    Returns basic statistics about traffic situation.
    - Logs DB connection, branch selection (summary/streets/route), query timings and transform timings.
    - Validates dates and inputs; maps DB/driver errors to 5xx; returns 404 when no data.
    """
    extras = request_extras(request)
    connection: Optional[psycopg2.extensions.connection] = None
    cursor: Optional[psycopg2.extensions.cursor] = None
    whole = Stopwatch()

    # --- 1) Validate/parse dates ---
    try:
        from_date = datetime.strptime(body.from_date, "%Y-%m-%d")
        to_date = datetime.strptime(body.to_date, "%Y-%m-%d") + timedelta(days=1)  # include whole 'to' day
    except Exception:
        logger.warning("[data_for_plot_drawer] Invalid date format. Expected YYYY-MM-DD.", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if from_date >= to_date:
        logger.warning(
            f"[data_for_plot_drawer] Invalid date range: from={from_date.isoformat()} >= to={to_date.isoformat()}",
            extra=extras | {"status": 400},
        )
        raise HTTPException(status_code=400, detail="'from_date' must be before 'to_date'.")

    streets = body.streets or []
    route = body.route or []

    logger.info(
        f"[data_for_plot_drawer] Input parsed: range={from_date.date()}..{(to_date - timedelta(days=1)).date()} "
        f"streets={len(streets)} route_points={len(route)}",
        extra=extras,
    )

    try:
        connection = get_db_connection(name)
        logger.info(
            f"[data_for_plot_drawer] DB connection established: {safe_dsn_from_connection(connection)}",
            extra=extras,
        )
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        rows = []
        if not streets and not route:
            logger.info("[data_for_plot_drawer] Branch: summary stats", extra=extras)
            qsw = Stopwatch()
            rows = fetch_sum_statistics(cursor, from_date, to_date)
            logger.info(
                f"[data_for_plot_drawer] Summary query executed; rows={len(rows)}",
                extra=extras | {"duration_ms": qsw.ms()},
            )

        elif streets and not route:
            if not all(isinstance(s, str) and s.strip() for s in streets):
                logger.warning("[data_for_plot_drawer] Invalid 'streets' list.", extra=extras | {"status": 400})
                raise HTTPException(status_code=400, detail="Invalid 'streets' list.")
            logger.info(f"[data_for_plot_drawer] Branch: hourly by streets (count={len(streets)})", extra=extras)
            qsw = Stopwatch()
            rows = fetch_hourly_by_streets(cursor, from_date, to_date, streets)
            logger.info(
                f"[data_for_plot_drawer] Streets query executed; rows={len(rows)}",
                extra=extras | {"duration_ms": qsw.ms()},
            )

        else:
            # route has priority if present
            if not isinstance(route, list) or len(route) < 2:
                logger.warning("[data_for_plot_drawer] Route must contain at least two points.", extra=extras | {"status": 400})
                raise HTTPException(status_code=400, detail="Route must contain at least two points.")
            logger.info(f"[data_for_plot_drawer] Branch: hourly by route (points={len(route)})", extra=extras)
            qsw = Stopwatch()
            rows = fetch_hourly_by_route(cursor, from_date, to_date, route)
            logger.info(
                f"[data_for_plot_drawer] Route query executed; rows={len(rows)}",
                extra=extras | {"duration_ms": qsw.ms()},
            )

        if not rows:
            logger.warning("[data_for_plot_drawer] No data found for the selected parameters.", extra=extras | {"status": 404})
            raise HTTPException(status_code=404, detail="No data found for the selected parameters.")

        # --- 3) Transform + return ---
        tsw = Stopwatch()
        data_jams, data_alerts, time, speedKMH, delay, level, length = transform_sum_statistics_to_legacy_format(
            rows, from_date, to_date
        )

        logger.info(
            f"[data_for_plot_drawer] Transform completed; items={len(time)}",
            extra=extras | {"duration_ms": tsw.ms()},
        )
        payload = {
            "jams": data_jams,
            "alerts": data_alerts,
            "speedKMH": speedKMH,
            "delay": delay,
            "level": level,
            "length": length,
            "xaxis": time,
        }
        return LegacyPlotResponse(**payload)

    except HTTPException:
        # already logged above
        raise

    except psycopg2.OperationalError as e:
        logger.exception(f"[data_for_plot_drawer] OperationalError: {e}", extra=extras | {"status": 503})
        raise HTTPException(status_code=503, detail="Database unavailable")

    except psycopg2.Error as e:
        logger.exception(f"[data_for_plot_drawer] psycopg2 error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Query execution error")

    except Exception as e:
        logger.exception(f"[data_for_plot_drawer] Unexpected error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            logger.exception("[data_for_plot_drawer] Failed to close cursor", extra=extras)
        try:
            if connection is not None:
                connection.close()
                logger.info(
                    f"[data_for_plot_drawer] DB connection closed; total handler time {whole.ms()} ms",
                    extra=extras | {"duration_ms": whole.ms()},
                )
        except Exception:
            logger.exception("[data_for_plot_drawer] Failed to close connection", extra=extras)


@router.post("/{name}/total_stats/", response_model=TotalStatsResponse)
async def total_stats(name: str, body: PlotDataRequestBody, request: Request):
    """
    Compute total statistics for the given interval (and optional streets/route filters).
    No hourly grouping; one aggregated row returned.
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
        logger.warning("[total_stats] Invalid date format. Expected YYYY-MM-DD.", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    if from_date >= to_date:
        logger.warning(f"[total_stats] Invalid date range: {from_date}..{to_date}", extra=extras | {"status": 400})
        raise HTTPException(status_code=400, detail="'from_date' must be before 'to_date'.")

    streets = body.streets or []
    route = body.route or []

    # 2) DB & fetch totals
    try:
        connection = get_db_connection(name)
        logger.info(f"[total_stats] DB connection established: {safe_dsn_from_connection(connection)}", extra=extras)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        qsw = Stopwatch()
        totals = fetch_total_statistics(cursor, from_date, to_date, streets=streets, route=route)
        logger.info(f"[total_stats] Totals computed", extra=extras | {"duration_ms": qsw.ms()})

        payload = TotalStatsResponse(**totals)
        logger.info(
            f"[total_stats] Result jams={payload.data_jams} alerts={payload.data_alerts}",
            extra=extras
        )
        return payload

    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        logger.exception(f"[total_stats] OperationalError: {e}", extra=extras | {"status": 503})
        raise HTTPException(status_code=503, detail="Database unavailable")
    except psycopg2.Error as e:
        logger.exception(f"[total_stats] psycopg2 error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Query execution error")
    except Exception as e:
        logger.exception(f"[total_stats] Unexpected error: {e}", extra=extras | {"status": 500})
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            logger.exception("[total_stats] Failed to close cursor", extra=extras)
        try:
            if connection is not None:
                connection.close()
                logger.info(
                    f"[total_stats] DB connection closed; total handler time {whole.ms()} ms",
                    extra=extras | {"duration_ms": whole.ms()},
                )
        except Exception:
            logger.exception("[total_stats] Failed to close connection", extra=extras)
