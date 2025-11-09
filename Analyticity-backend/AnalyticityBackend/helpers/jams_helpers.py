import binascii
import logging
import time
from typing import Optional, List

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

import geopandas as gpd
from shapely import wkt
from shapely import from_wkb
from shapely.strtree import STRtree
from shapely.errors import GEOSException
from shapely.geometry.base import BaseGeometry
from shapely.prepared import prep


def _filter_streets(streets_gdf: gpd.GeoDataFrame, streets: List[str]) -> gpd.GeoDataFrame:
    """Filter streets by names safely; if empty list, return all."""
    if not streets:
        return streets_gdf
    return streets_gdf[streets_gdf["nazev"].isin(streets)].copy()


def _parse_wkb_any(v) -> Optional["BaseGeometry"]:
    """
    Robustly parse WKB coming from Postgres (bytea) regardless of adaptation:
    - bytes / memoryview  -> direct
    - str starting with '\\x' (hex) -> unhexlify
    - None / empty -> returns None
    Raises GEOSException only if content looks like bytes but is invalid.
    """
    if v is None:
        return None
    try:
        if isinstance(v, memoryview):
            v = bytes(v)
        if isinstance(v, bytes):
            if len(v) == 0:
                return None
            return from_wkb(v)
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return None
            # Hex text representation of bytea: '\xDEADBEEF...'
            if s.startswith("\\x") or s.startswith("\x5c\x78"):  # defensive
                try:
                    raw = binascii.unhexlify(s[2:])
                except binascii.Error as e:
                    raise GEOSException(f"Invalid HEX WKB: {e}") from e
                return from_wkb(raw)
            # As a last resort, some drivers may accidentally send WKT in 'wkb' column
            # Try WKT parse to avoid hard failure:
            try:
                return wkt.loads(s)
            except Exception:
                raise GEOSException("String is neither HEX WKB nor WKT.")
        # Unknown type
        raise GEOSException(f"Unsupported WKB type: {type(v)}")
    except GEOSException:
        raise
    except Exception as e:
        # Normalize unexpected errors into GEOSException to handle upstream uniformly
        raise GEOSException(str(e)) from e


def _build_jams_gdf(rows: list, logger) -> gpd.GeoDataFrame:
    """
    Create a GeoDataFrame from DB rows.
    Prefers 'wkb' (bytea) but accepts 'wkt' fallback.
    Skips invalid/NULL geometries with warnings instead of crashing.
    """
    if not rows:
        return gpd.GeoDataFrame(columns=["street", "geometry"], geometry="geometry", crs="EPSG:4326")

    df = pd.DataFrame(rows)

    geoms = []
    skipped = 0
    first_err_sample = None

    if "wkb" in df.columns:
        for v in df["wkb"].tolist():
            try:
                geom = _parse_wkb_any(v)
                if geom is None:
                    skipped += 1
                geoms.append(geom)
            except GEOSException as e:
                skipped += 1
                if first_err_sample is None:
                    first_err_sample = (type(v).__name__, str(e))
                geoms.append(None)
    elif "wkt" in df.columns:
        for v in df["wkt"].tolist():
            try:
                if v is None or str(v).strip() == "":
                    skipped += 1
                    geoms.append(None)
                else:
                    geoms.append(wkt.loads(v))
            except Exception as e:
                skipped += 1
                if first_err_sample is None:
                    first_err_sample = ("str", str(e))
                geoms.append(None)
    else:
        raise HTTPException(status_code=500, detail="Missing geometry column (expected 'wkb' or 'wkt').")

    if skipped:
        logger.warning(
            f"[jams] Skipped {skipped} invalid/NULL geometries while parsing jams"
            + (f"; first_error={first_err_sample}" if first_err_sample else ""),
            extra={"request_id": "", "path": "/parse", "method": "INTERNAL"},
        )

    df["geometry"] = geoms
    gdf = gpd.GeoDataFrame(df[df["geometry"].notnull()].copy(), geometry="geometry", crs="EPSG:4326")

    if gdf.empty:
        logger.warning(
            "[jams] All geometries were NULL/invalid after parsing.",
            extra={"request_id": "", "path": "/parse", "method": "INTERNAL"},
        )

    return gdf

# nastaviteľná tolerancia v metroch
TOLERANCE_M = 15  # tip: 10–20 m funguje dobre v meste
PROJECTED_CRS = "EPSG:3857"  # metrické; alebo CZ presne: "EPSG:5514"


def _count_with_strtree_tolerant(street_gdf: gpd.GeoDataFrame,
                                 jams_gdf: gpd.GeoDataFrame,
                                 logger=None,
                                 tol_m: float = TOLERANCE_M) -> gpd.GeoDataFrame:
    """
    Count jams within a tolerance (in meters) around each street.
    Uses Shapely STRtree and prepared geometries.
    Handles invalid geometries and NaN values gracefully.
    Filters jams by matching street names.
    """

    # --- make sure tolerance is float ---
    try:
        tol_m = float(tol_m)
    except Exception:
        tol_m = TOLERANCE_M
        if logger:
            logger.warning(f"[jams] Invalid tolerance input; defaulting to {TOLERANCE_M}m")

    if tol_m <= 0:
        if logger:
            logger.warning("[jams] Non-positive tolerance; forcing to 1m")
        tol_m = 1.0

    if street_gdf.empty or jams_gdf.empty:
        out = street_gdf.copy()
        out["count"] = 0
        return out

    sg = street_gdf.copy()
    jg = jams_gdf.copy()

    # ensure CRS
    if sg.crs is None:
        sg.set_crs("EPSG:4326", inplace=True)
    if jg.crs is None:
        jg.set_crs("EPSG:4326", inplace=True)

    # project to metric CRS
    if sg.crs.to_string() != PROJECTED_CRS:
        sg = sg.to_crs(PROJECTED_CRS)
    if jg.crs.to_string() != PROJECTED_CRS:
        jg = jg.to_crs(PROJECTED_CRS)

    # validate geometries (no NaN, None, empty)
    def _valid(g):
        if g is None or not isinstance(g, BaseGeometry):
            return False
        if g.is_empty:
            return False
        coords = np.array(g.coords) if hasattr(g, "coords") else None
        if coords is not None and not np.isfinite(coords).all():
            return False
        return True

    sg = sg[sg["geometry"].apply(_valid)].copy()
    jg = jg[jg["geometry"].apply(_valid)].copy()

    if sg.empty or jg.empty:
        out = street_gdf.copy()
        out["count"] = 0
        return out

    # build spatial index and jam geometry to street name mapping
    jam_geoms = jg["geometry"].tolist()
    sindex = STRtree(jam_geoms)

    # Create mapping from jam geometry to street name for filtering
    jam_street_map = {}
    for idx, row in jg.iterrows():
        jam_street_map[id(row["geometry"])] = row.get("street", "")

    if logger:
        logger.info(
            f"[jams] Counting: {len(sg)} streets, {len(jg)} jams, tolerance={tol_m}m",
            extra={"request_id": "", "path": "/count", "method": "INTERNAL"}
        )
        # Sample street names from jams
        sample_jam_streets = list(set([v for v in jam_street_map.values() if v]))[:5]
        sample_street_names = sg["nazev"].head(5).tolist()
        logger.info(
            f"[jams] Sample jam streets: {sample_jam_streets}",
            extra={"request_id": "", "path": "/count", "method": "INTERNAL"}
        )
        logger.info(
            f"[jams] Sample street names: {sample_street_names}",
            extra={"request_id": "", "path": "/count", "method": "INTERNAL"}
        )

    counts = []
    matched_pairs = []  # for debugging
    for idx, street_row in sg.iterrows():
        geom = street_row["geometry"]
        street_name = street_row.get("nazev", "")

        if not _valid(geom):
            counts.append(0)
            continue

        try:
            # expand search area slightly (tolerance)
            search_env = geom.buffer(float(tol_m)).envelope
        except Exception as e:
            if logger:
                logger.warning(f"[jams] Failed buffering geometry: {e}")
            counts.append(0)
            continue

        # candidate geometries from index
        cand = sindex.query(search_env)

        # prepare geometry for fast intersection
        prepped = prep(geom.buffer(float(tol_m)))
        c = 0
        for g in cand:
            if not _valid(g):
                continue
            # Check if jam intersects with street geometry
            if not prepped.intersects(g):
                continue
            # Match street names (case-insensitive, handle None/empty)
            jam_street = jam_street_map.get(id(g), "")
            if jam_street and street_name:
                if jam_street.lower().strip() == street_name.lower().strip():
                    c += 1
                    if len(matched_pairs) < 10:  # Store first 10 matches for debugging
                        matched_pairs.append((street_name, jam_street))
            elif not jam_street and not street_name:
                # Both empty - could be a match, but safer to skip
                pass
        counts.append(c)

    out = sg.copy()
    out["count"] = counts

    if logger:
        total_matches = sum(counts)
        streets_with_jams = sum(1 for c in counts if c > 0)
        logger.info(
            f"[jams] Counting done: {total_matches} total matches, {streets_with_jams}/{len(counts)} streets with jams",
            extra={"request_id": "", "path": "/count", "method": "INTERNAL"}
        )
        if matched_pairs:
            logger.info(
                f"[jams] Sample matched pairs: {matched_pairs[:5]}",
                extra={"request_id": "", "path": "/count", "method": "INTERNAL"}
            )

    # reproject back to EPSG:4326 if needed
    if out.crs.to_string() != street_gdf.crs.to_string():
        out = out.to_crs(street_gdf.crs)

    return out


import geopandas as gpd
from shapely.strtree import STRtree
from shapely.geometry import LineString, MultiLineString
from shapely.ops import transform
import pyproj


def count_delays_by_parts(gdf: gpd.GeoDataFrame, data: gpd.GeoDataFrame, tolerance_m: float = 10):
    """
    Count how many jam geometries (data) intersect each street (gdf) using STRtree for speed,
    but respecting street names and allowing small spatial tolerance in meters.
    """

    if gdf.empty or data.empty:
        gdf["count"] = 0
        return _assign_color(gdf)

    # --- prepare projection to metric CRS (so we can buffer in meters) ---
    to_m = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
    to_deg = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform

    gdf_m = gdf.copy()
    gdf_m["geometry"] = gdf_m["geometry"].apply(lambda g: transform(to_m, g))

    data_m = data.copy()
    data_m["geometry"] = data_m["geometry"].apply(lambda g: transform(to_m, g))

    # --- build STRtree once for jams ---
    jam_geoms = data_m["geometry"].tolist()
    jam_index = STRtree(jam_geoms)

    # map jam geometry → street name for filtering
    jam_name_map = {row["geometry"]: row["street"] for _, row in data_m.iterrows()}

    counts = []

    for idx, street_row in gdf_m.iterrows():
        street_name = street_row["nazev"]
        street_geom = street_row["geometry"]

        if street_geom is None or street_geom.is_empty:
            counts.append(0)
            continue

        # expand street geometry by tolerance (in meters)
        street_buffer = street_geom.buffer(tolerance_m)

        # candidate jams by bounding box match
        candidates = jam_index.query(street_buffer)

        # count only jams with the same street name
        c = 0
        for cand_geom in candidates:
            if jam_name_map.get(cand_geom) != street_name:
                continue
            # final precise check
            if street_buffer.intersects(cand_geom):
                c += 1

        counts.append(c)

    # store results
    gdf_m["count"] = counts

    # reproject back to EPSG:4326 (WGS84)
    gdf_m["geometry"] = gdf_m["geometry"].apply(lambda g: transform(to_deg, g))

    return _assign_color(gdf_m)


def _assign_color(count: int, num_days: int = 7) -> str:
    """
    Apply your color thresholds inline (same logic as in your helper).
    - Keep thresholds compatible with your existing FE expectations.
    """
    GREEN_COLOR = 1
    ORANGE_COLOR = 3
    if count < GREEN_COLOR * num_days:
        return "green"
    if count <= ORANGE_COLOR * num_days:
        return "orange"
    return "red"


def _serialize_street_paths(df_streets: gpd.GeoDataFrame) -> list:
    """
    Serialize to your existing output format:
    [{ 'street_name': ..., 'path': [[lon, lat], ...], 'color': ... }, ...]
    """
    out = []
    for _, row in df_streets.iterrows():
        geom = row["geometry"]
        if geom is None:
            continue
        # Support LineString and MultiLineString
        if geom.geom_type == "LineString":
            coords = list(geom.coords)
        elif geom.geom_type == "MultiLineString":
            coords = [xy for line in geom.geoms for xy in line.coords]
        else:
            continue
        out.append(
            {
                "street_name": row.get("nazev"),
                # Leaflet expects [lat, lon] instead of [lon, lat]
                "path": [[lat, lon] for lon, lat in coords],
                "color": row.get("color", "green"),
            }
        )
    return out
