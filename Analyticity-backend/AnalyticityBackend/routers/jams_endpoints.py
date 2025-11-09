import logging
import time
from typing import Optional

import psycopg2
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request
from psycopg2.extras import RealDictCursor

import geopandas as gpd

from constants.queries import QUERY_JAMS
from db_config import get_db_connection
from models.request_models import PlotDataRequestBody

from helpers.jams_helpers import _filter_streets, _assign_color, _count_with_strtree_tolerant, \
    _build_jams_gdf, _serialize_street_paths

router = APIRouter(tags=["jams"])
logger = logging.getLogger("app.jams")

# -----------------------------------------------------------------------------------------
# Load streets GeoJSON ONCE (cached)
# -----------------------------------------------------------------------------------------
_STREETS_GDF: Optional[gpd.GeoDataFrame] = None
_STREETS_LOAD_MS: Optional[int] = None


def _load_streets_once( path: str = "./datasets/streets_exploded.geojson") -> gpd.GeoDataFrame:
    """Load streets layer once and cache it in memory."""
    global _STREETS_GDF, _STREETS_LOAD_MS
    if _STREETS_GDF is not None:
        return _STREETS_GDF
    t0 = time.perf_counter()
    gdf = gpd.read_file(path)
    if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    _STREETS_GDF = gdf
    _STREETS_LOAD_MS = int((time.perf_counter() - t0) * 1000)
    logger.info(
        f"[jams] Streets GeoJSON loaded; rows={len(gdf)} in {_STREETS_LOAD_MS} ms",
        extra={"request_id": "", "path": "/init", "method": "INIT"},
    )
    return _STREETS_GDF


@router.post("/{name}/all_delays/")
async def get_all_delays_for_drawing(name: str, body: PlotDataRequestBody, request: Request):
    """
    Function returns delays from Waze for a given time interval.
    Request model stays UNCHANGED:
      class PlotDataRequestBody(BaseModel):
          from_date: str | None
          to_date: str | None
          streets: Union[List[str], None]
          route: Union[List[List[float]], None]
    """
    request_id = getattr(request.state, "request_id", "unknown")
    t_all = time.perf_counter()

    # Load streets layer (cached)
    try:
        streets_gdf = _load_streets_once()
    except Exception as e:
        logger.exception(
            f"[jams] Failed to load streets layer: {e}",
            extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 500},
        )
        raise HTTPException(status_code=500, detail="Failed to load streets layer.")

    # Parse dates (remain strings in model; validated here)
    try:
        from_date = datetime.strptime(body.from_date, "%Y-%m-%d") if body.from_date else None
        to_date = datetime.strptime(body.to_date, "%Y-%m-%d") + timedelta(days=1) if body.to_date else None
        if not from_date or not to_date:
            raise ValueError("from_date/to_date required")
    except Exception:
        logger.warning(
            "[jams] Invalid or missing date(s); expected YYYY-MM-DD for both from_date and to_date.",
            extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 400},
        )
        raise HTTPException(status_code=400, detail="Invalid or missing dates. Use YYYY-MM-DD for both.")

    streets_list = body.streets or []
    route = body.route or []  # not used in current logic, preserved for compatibility

    filtered_streets_gdf = _filter_streets(streets_gdf, streets_list)

    logger.info(
        "[jams] Input parsed",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": "POST",
            "from": body.from_date,
            "to": body.to_date,
            "streets_count": len(streets_list),
            "filtered_streets_rows": len(filtered_streets_gdf),
        },
    )

    connection: Optional[psycopg2.extensions.connection] = None
    cursor: Optional[psycopg2.extensions.cursor] = None

    try:
        # DB fetch
        connection = get_db_connection(name)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        t_db = time.perf_counter()
        cursor.execute(QUERY_JAMS, (from_date, to_date))
        rows = cursor.fetchall()
        db_ms = int((time.perf_counter() - t_db) * 1000)

        logger.info(
            f"[jams] DB query executed in {db_ms} ms; rows={len(rows)}",
            extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
        )

        # Log sample street names from jams data
        if rows:
            sample_streets = [r.get("street", "") for r in rows[:10]]
            unique_streets = list(set([r.get("street", "") for r in rows if r.get("street")]))[:10]
            logger.info(
                f"[jams] Sample jam streets from DB: {sample_streets}",
                extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
            )
            logger.info(
                f"[jams] Unique streets in jams (sample): {unique_streets}",
                extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
            )

        if not rows:
            logger.warning(
                "[jams] No data found for the selected parameters.",
                extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 404},
            )
            raise HTTPException(status_code=404, detail="No data found for the selected parameters.")

        # Build jams GDF (supports WKB/WKT)
        t_geo = time.perf_counter()
        jams_gdf = _build_jams_gdf(rows, logger)
        geo_ms = int((time.perf_counter() - t_geo) * 1000)

        # Spatial counting via STRtree
        t_cnt = time.perf_counter()
        counted = _count_with_strtree_tolerant(filtered_streets_gdf, jams_gdf, logger)
        count_ms = int((time.perf_counter() - t_cnt) * 1000)

        # Assign color (same thresholds as before)
        counted = counted.copy()
        counted["color"] = counted["count"].apply(_assign_color)

        # Serialize to your original response shape
        t_ser = time.perf_counter()
        response = _serialize_street_paths(counted)
        ser_ms = int((time.perf_counter() - t_ser) * 1000)

        total_ms = int((time.perf_counter() - t_all) * 1000)
        logger.info(
            f"[jams] OK - db:{db_ms}ms geo:{geo_ms}ms count:{count_ms}ms ser:{ser_ms}ms total:{total_ms}ms "
            f"payload_items={len(response)}",
            extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 200},
        )

        return response

    except HTTPException:
        raise

    except psycopg2.OperationalError as e:
        logger.exception(
            f"[jams] OperationalError: {e}",
            extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 503},
        )
        raise HTTPException(status_code=503, detail="Database unavailable")

    except psycopg2.Error as e:
        logger.exception(
            f"[jams] Database query error: {e}",
            extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 500},
        )
        raise HTTPException(status_code=500, detail="Database query error")

    except Exception as e:
        logger.exception(
            f"[jams] Unexpected error: {e}",
            extra={"request_id": request_id, "path": request.url.path, "method": "POST", "status": 500},
        )
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        except Exception:
            logger.exception(
                "[jams] Failed to close DB resources",
                extra={"request_id": request_id, "path": request.url.path, "method": "POST"},
            )
