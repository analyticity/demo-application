from constants.queries import QUERY_SUM_STATISTICS, QUERY_SUM_STATISTICS_WITH_STREETS,\
    QUERY_SUM_STATISTICS_WITH_ROUTE, \
    QUERY_TOTAL_STATISTICS, QUERY_TOTAL_STATISTICS_WITH_STREETS, \
    QUERY_TOTAL_STATISTICS_WITH_ROUTE
from fastapi import HTTPException
from helpers.universal_helpers import convert_utc_to_local
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Tuple, Optional, Dict, Any


def transform_sum_statistics_to_legacy_format(
    rows: Iterable[dict],
    from_date: datetime,
    to_date: datetime,
    *,
    now_utc: Optional[datetime] = None,
) -> Tuple[List[int], List[int], List[int], List[float], List[float], List[float], List[float]]:
    """
    Convert rows (from QUERY_SUM_STATISTICS) into the legacy tuple-of-lists format:

        (data_jams, data_alerts, pubMillis, speedKMH, delay, level, length)

    Matching legacy behavior:
    - Build hourly axis for [from_date, to_date) and drop future hours.
    - For hours with no jams:
        * length=0.0 km, level=0.0, delay=0.0 min, speedKMH=35.0 (legacy default)
      (even if alerts exist in that hour)
    - Round numeric values to 2 decimals; convert delay from seconds->minutes, length m->km.
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    def ensure_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    from_utc = ensure_utc(from_date).replace(minute=0, second=0, microsecond=0)
    to_utc = ensure_utc(to_date).replace(minute=0, second=0, microsecond=0)
    now_floor = now_utc.replace(minute=0, second=0, microsecond=0)

    # Index DB rows by their hour (truncate to hour)
    by_hour = {}
    for r in rows:
        t: datetime = r["utc_time"]
        t = ensure_utc(t).replace(minute=0, second=0, microsecond=0)
        by_hour[t] = {
            "data_jams": int(r["data_jams"]) if r.get("data_jams") is not None else 0,
            "data_alerts": int(r["data_alerts"]) if r.get("data_alerts") is not None else 0,
            # keep raw values (may be None) – we decide defaults below
            "length_m": r.get("length"),
            "level": r.get("level"),
            "delay_s": r.get("delay"),
            "speed_kmh": r.get("speedKMH"),
        }

    # Build complete hourly axis (exclusive of to_utc) and exclude future hours
    axis = []
    cur = from_utc
    while cur < to_utc and cur <= now_floor:
        axis.append(cur)
        cur += timedelta(hours=1)

    data_jams: List[int] = []
    data_alerts: List[int] = []
    pubMillis: List[int] = []
    speedKMH: List[float] = []
    delay: List[float] = []
    level: List[float] = []
    length: List[float] = []

    for t in axis:
        rec = by_hour.get(t)

        if rec is None:
            # No row at all -> legacy defaults
            jams = 0
            alerts = 0
            _length_km = 0.0
            _level = 0.0
            _delay_min = 0.0
            _speed = 35.0
        else:
            jams = rec["data_jams"]
            alerts = rec["data_alerts"]

            # If there are no jams in this hour, legacy code used defaults for jam-derived metrics.
            if jams == 0:
                _length_km = 0.0
                _level = 0.0
                _delay_min = 0.0
                _speed = 35.0
            else:
                # Convert and round jam-derived metrics
                _length_km = round(float(rec["length_m"]) / 1000.0, 2) if rec["length_m"] is not None else 0.0
                _level = round(float(rec["level"]), 2) if rec["level"] is not None else 0.0
                _delay_min = round(float(rec["delay_s"]) / 60.0, 2) if rec["delay_s"] is not None else 0.0
                _speed = round(float(rec["speed_kmh"]), 2) if rec["speed_kmh"] is not None else 35.0

        data_jams.append(jams)
        data_alerts.append(alerts)
        pubMillis.append(int(t.timestamp() * 1000))  # unix ms
        speedKMH.append(round(_speed, 2))
        delay.append(round(_delay_min, 2))
        level.append(round(_level, 2))
        length.append(round(_length_km, 2))

    return data_jams, data_alerts, pubMillis, speedKMH, delay, level, length


def fetch_sum_statistics(cursor, from_date, to_date):
    """
    Returns per-hour global statistics across the whole area for [from_date, to_date).
    Uses a generated hourly axis to ensure hours without jams/alerts are included.
    """
    cursor.execute(
        QUERY_SUM_STATISTICS,
        (from_date, to_date,  # hours CTE
         from_date, to_date,  # jams_agg
         from_date, to_date)  # alerts_agg
    )
    return cursor.fetchall()

def fetch_hourly_by_streets(cursor, from_date, to_date, streets: List[str]):
    """
    Function returns statistics for given list of streets

    :param cursor:
    :param from_date:
    :param to_date:
    :param streets:
    :return:
    """
    cursor.execute(
        QUERY_SUM_STATISTICS_WITH_STREETS,
        (from_date, to_date,  # for alerts subquery
         from_date, to_date, streets)  # for jams main query
    )
    return cursor.fetchall()


def fetch_hourly_by_route(cursor, from_date, to_date, route_coords):
    """
    Fetch traffic stats by spatial proximity to a given route.
    """
    linestring = "LINESTRING(" + ", ".join([f"{lon} {lat}" for lon, lat in route_coords]) + ")"

    params = (
        linestring, from_date, to_date,   # For alerts
        linestring, from_date, to_date,  # For jams
    )

    cursor.execute(QUERY_SUM_STATISTICS_WITH_ROUTE, params)
    return cursor.fetchall()


def transform_to_response_statistics(rows):
    """
    Function transforms the result to the format accepted by (original) FE application

    :param rows:
    :return:
    """
    data_jams = []
    data_alerts = []
    speedKMH = []
    delay = []
    level = []
    length = []
    xaxis = []


    if not rows:
        raise ValueError("Query returned no rows")

    else:
        for row in rows:
            data_jams.append(row["data_jams"])
            data_alerts.append(row["data_alerts"])
            speedKMH.append(row["speedkmh"])
            delay.append(row["delay"])
            level.append(row["level"])
            length.append(row["length"])
            xaxis.append(convert_utc_to_local(row["utc_time"]))

    return {
        "jams": data_jams,
        "alerts": data_alerts,
        "speedKMH": speedKMH,
        "delay": delay,
        "level": level,
        "length": length,
        "xaxis": xaxis
    }


def transform_to_response_statistics_v2(rows):
    """
    Transforms the query result into a structure that is more suitable for the frontend application.
    Each timestamp will have its own object containing all statistics.

    :param rows: List of rows returned from the database query
    :return: A dictionary of timestamped statistics
    """
    statistics = []

    for row in rows:
        timestamp = convert_utc_to_local(row["utc_time"])
        statistics.append({
            "timestamp": timestamp,
            "stats": {
                "jams": row["data_jams"],
                "alerts": row["data_alerts"],
                "speedKMH": row["speedkmh"],
                "delay": row["delay"],
                "level": row["level"],
                "length": row["length"]
            }
        })

    return statistics


def _build_linestring(route: List[List[float]]) -> str:
    """Build WKT LINESTRING from [[lon,lat], ...]; validates coords."""
    if not isinstance(route, list) or len(route) < 2:
        raise HTTPException(status_code=400, detail="Route must contain at least two points.")
    parts = []
    for idx, pair in enumerate(route):
        try:
            lon, lat = float(pair[0]), float(pair[1])
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid route coordinate at index {idx}")
        parts.append(f"{lon} {lat}")
    return "LINESTRING(" + ", ".join(parts) + ")"


def fetch_total_statistics(
    cursor,
    from_date: datetime,
    to_date: datetime,
    streets: Optional[List[str]] = None,
    route: Optional[List[List[float]]] = None,
) -> Dict[str, Any]:
    """
    Returns single-row totals for the selected scope.
    - Without filters -> full area totals
    - With streets -> filter jams/alerts by street IN (..)
    - With route   -> spatial filter using ST_Intersects on LINESTRING
    """
    streets = streets or []
    route = route or []

    if streets and route:
        raise HTTPException(status_code=400, detail="Provide either 'streets' or 'route', not both.")

    if route:
        linestring = _build_linestring(route)
        cursor.execute(
            QUERY_TOTAL_STATISTICS_WITH_ROUTE,
            (
                linestring,           # route geom
                from_date, to_date,   # alerts window
                from_date, to_date,   # jams window
            ),
        )
    elif streets:
        cursor.execute(
            QUERY_TOTAL_STATISTICS_WITH_STREETS,
            (
                from_date, to_date,   # alerts window
                streets,              # alerts streets
                from_date, to_date,   # jams window
                streets,              # jams streets
            ),
        )
    else:
        cursor.execute(
            QUERY_TOTAL_STATISTICS,
            (
                from_date, to_date,   # alerts window
                from_date, to_date,   # jams window
            ),
        )

    row = cursor.fetchone() or {}
    # Normalize None -> defaults if there are no jams in the interval
    data_jams = int(row.get("data_jams") or 0)
    data_alerts = int(row.get("data_alerts") or 0)

    if data_jams == 0:
        return {
            "data_jams": 0,
            "data_alerts": data_alerts,
            "speedKMH": 35.0,
            "delay": 0.0,
            "level": 0.0,
            "length": 0.0,
        }

    return {
        "data_jams": data_jams,
        "data_alerts": data_alerts,
        "speedKMH": float(row.get("speedKMH") or 35.0),
        "delay": round(float(row.get("delay") or 0.0), 2),
        "level": round(float(row.get("level") or 0.0), 2),
        "length": round(float(row.get("length") or 0.0), 2),
    }