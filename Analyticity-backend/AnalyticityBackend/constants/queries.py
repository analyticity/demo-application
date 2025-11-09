QUERY_SUM_STATISTICS = """
WITH hours AS (
    SELECT generate_series(
        date_trunc('hour', %s::timestamptz),
        date_trunc('hour', %s::timestamptz) - interval '1 hour',
        interval '1 hour'
    ) AS utc_time
),
jams_agg AS (
    SELECT
        date_trunc('hour', published_at AT TIME ZONE 'UTC') AS utc_time,
        COUNT(*)                          AS data_jams,
        AVG(speed_kmh_avg)::FLOAT         AS speedKMH,
        AVG(delay_avg)::FLOAT             AS delay,
        AVG(jam_level_avg)::FLOAT         AS level,
        AVG(jam_length_avg)::FLOAT        AS length
    FROM jams
    WHERE published_at >= %s AND published_at < %s
    GROUP BY utc_time
),
alerts_agg AS (
    SELECT
        date_trunc('hour', published_at AT TIME ZONE 'UTC') AS utc_time,
        COUNT(*)                          AS data_alerts
    FROM alerts
    WHERE published_at >= %s AND published_at < %s
    GROUP BY utc_time
)
SELECT
    j.data_jams,
    j.speedKMH,
    j.delay,
    j.level,
    j.length,
    h.utc_time,
    COALESCE(a.data_alerts, 0)            AS data_alerts
FROM hours h
LEFT JOIN jams_agg   j USING (utc_time)
LEFT JOIN alerts_agg a USING (utc_time)
ORDER BY h.utc_time;
"""

QUERY_SUM_STATISTICS_WITH_STREETS = """
       SELECT 
            COUNT(*) AS data_jams,
            AVG(speed_kmh_avg)::FLOAT AS speedKMH,
            AVG(delay_avg)::FLOAT AS delay,
            AVG(jam_level_avg)::FLOAT AS level,
            AVG(jam_length_avg)::FLOAT AS length,
            published_at AT TIME ZONE 'UTC' AS utc_time,
            (
                SELECT COUNT(*) 
                FROM alerts 
                WHERE published_at >= %s AND published_at < %s
            ) AS data_alerts
        FROM jams
        WHERE published_at >= %s AND published_at < %s
          AND street = ANY(%s)
        GROUP BY utc_time
        ORDER BY utc_time
    """

QUERY_SUM_STATISTICS_WITH_ROUTE = """
        SELECT 
            COUNT(*) AS data_jams,
            AVG(speed_kmh_avg)::FLOAT AS speedKMH,
            AVG(delay_avg)::FLOAT AS delay,
            AVG(jam_level_avg)::FLOAT AS level,
            AVG(jam_length_avg)::FLOAT AS length,
            published_at AT TIME ZONE 'UTC' AS utc_time,
            (
                SELECT COUNT(*) 
                FROM alerts 
                WHERE ST_DWithin(
                          location::geography,
                          ST_GeomFromText(%s, 4326)::geography,
                          20
                      )
                  AND published_at >= %s AND published_at < %s
            ) AS data_alerts
        FROM jams
        WHERE ST_DWithin(
                  jam_line::geography,
                  ST_GeomFromText(%s, 4326)::geography,
                  20
              )
          AND published_at >= %s AND published_at < %s
        GROUP BY utc_time
        ORDER BY utc_time
    """

QUERY_ALERTS = """
    SELECT
        uuid,
        street,
        type,
        subtype,
        EXTRACT(EPOCH FROM published_at) * 1000 AS pubMillis,
        ST_X(location::geometry) AS longitude,
        ST_Y(location::geometry) AS latitude
        FROM alerts
        WHERE published_at BETWEEN %s AND %s;
"""

QUERY_ALERTS_WITH_STREETS = """
    SELECT
        uuid,
        street,
        type,
        subtype,
        EXTRACT(EPOCH FROM published_at) * 1000 AS pubMillis,
        ST_X(location::geometry) AS longitude,
        ST_Y(location::geometry) AS latitude
        FROM alerts
        WHERE published_at BETWEEN %s AND %s 
            AND street = ANY(%s);
"""

QUERY_ALERTS_WITH_ROUTE = """
    SELECT
        uuid,
        street,
        type,
        subtype,
        EXTRACT(EPOCH FROM published_at) * 1000 AS pubMillis,
        ST_X(location::geometry) AS longitude,
        ST_Y(location::geometry) AS latitude
    FROM alerts
    WHERE published_at BETWEEN %s AND %s 
        AND ST_DWithin(
                location::geography,
                ST_GeomFromText(%s, 4326)::geography,
                20
            );
"""

QUERY_JAMS = """
    SELECT
        uuid,
        street,
        ST_AsEWKB(jam_line::geometry) AS wkb,
        jam_level_avg AS jam_level,
        delay_avg AS delay,
        published_at
    FROM
        jams
    WHERE published_at BETWEEN %s AND %s; 
"""

QUERY_TOP_N_STREETS = """
        SELECT street, COUNT(*)
        FROM %s
        WHERE published_at BETWEEN %s AND %s 
            AND street = ANY(%s); 
        GROUP BY street
        ORDER BY count DESC
        LIMIT %s;
"""

QUERY_TOP_N_ROUTE = """
        SELECT street, COUNT(*)
        FROM %s
        WHERE published_at BETWEEN %s AND %s 
            AND ST_DWithin(
                %s::geography,
                ST_GeomFromText(%s, 4326)::geography,
                20
            );
        GROUP BY street
        ORDER BY count DESC
        LIMIT %s;
"""

QUERY_TOTAL_STATISTICS = """
SELECT
    COUNT(*) AS data_jams,
    COALESCE(AVG(speed_kmh_avg)::FLOAT, 35.0)              AS speedKMH,  -- km/h
    COALESCE(SUM(delay_avg)::FLOAT / 60.0, 0.0)            AS delay,     -- minutes
    COALESCE(AVG(jam_level_avg)::FLOAT, 0.0)               AS level,
    COALESCE(SUM(jam_length_avg)::FLOAT / 1000.0, 0.0)     AS length,    -- km
    (
        SELECT COUNT(*)
        FROM alerts
        WHERE published_at >= %s AND published_at < %s
    ) AS data_alerts
FROM jams
WHERE published_at >= %s AND published_at < %s;
"""

# (B) Filtrovanie podľa ulíc (uprav, ak máš iný názov stĺpca ako "street")
QUERY_TOTAL_STATISTICS_WITH_STREETS = """
SELECT
    COUNT(*) AS data_jams,
    COALESCE(AVG(speed_kmh_avg)::FLOAT, 35.0)              AS speedKMH,
    COALESCE(AVG(delay_avg)::FLOAT / 60.0, 0.0)            AS delay,
    COALESCE(AVG(jam_level_avg)::FLOAT, 0.0)               AS level,
    COALESCE(AVG(jam_length_avg)::FLOAT / 1000.0, 0.0)     AS length,
    (
        SELECT COUNT(*)
        FROM alerts
        WHERE published_at >= %s AND published_at < %s
          AND street = ANY(%s)
    ) AS data_alerts
FROM jams
WHERE published_at >= %s AND published_at < %s
  AND street = ANY(%s);
"""

# (C) Filtrovanie podľa trasy (predpoklad: geom v SRID 4326). Zmeň názvy stĺpcov/SRID ak treba.
QUERY_TOTAL_STATISTICS_WITH_ROUTE = """
WITH route AS (
    SELECT ST_GeomFromText(%s, 4326) AS geom
)
SELECT
    COUNT(*) AS data_jams,
    COALESCE(AVG(j.speed_kmh_avg)::FLOAT, 35.0)              AS speedKMH,
    COALESCE(AVG(j.delay_avg)::FLOAT / 60.0, 0.0)            AS delay,
    COALESCE(AVG(j.jam_level_avg)::FLOAT, 0.0)               AS level,
    COALESCE(AVG(j.jam_length_avg)::FLOAT / 1000.0, 0.0)     AS length,
    (
        SELECT COUNT(*)
        FROM alerts a, route r
        WHERE a.published_at >= %s AND a.published_at < %s
          AND ST_Intersects(a.geom, r.geom)
    ) AS data_alerts
FROM jams j, route r
WHERE j.published_at >= %s AND j.published_at < %s
  AND ST_Intersects(j.geom, r.geom);
"""

QUERY_ALERTS_TYPES_BASE = """
SELECT
  a.type,
  COALESCE(NULLIF(a.subtype, ''), 'NOT_DEFINED') AS subtype,
  COUNT(*)::BIGINT AS count
FROM alerts a
WHERE a.published_at >= %s AND a.published_at < %s
GROUP BY a.type, COALESCE(NULLIF(a.subtype, ''), 'NOT_DEFINED');
"""

# Optional filter by streets (alerts.street = ANY($3))
QUERY_ALERTS_TYPES_WITH_STREETS = """
SELECT
  a.type,
  COALESCE(NULLIF(a.subtype, ''), 'NOT_DEFINED') AS subtype,
  COUNT(*)::BIGINT AS count
FROM alerts a
WHERE a.published_at >= %s AND a.published_at < %s
  AND a.street = ANY(%s)
GROUP BY a.type, COALESCE(NULLIF(a.subtype, ''), 'NOT_DEFINED');
"""

# JAMS: top-N streets in interval (drop NULL/empty streets)
QUERY_TOP_STREETS_JAMS_BASE = """
SELECT j.street, COUNT(*)::BIGINT AS cnt
FROM jams j
WHERE j.published_at >= %s AND j.published_at < %s
  AND NULLIF(TRIM(j.street), '') IS NOT NULL
GROUP BY j.street
ORDER BY cnt DESC, j.street ASC
LIMIT %s;
"""

# JAMS with explicit streets allowlist
QUERY_TOP_STREETS_JAMS_WITH_STREETS = """
SELECT j.street, COUNT(*)::BIGINT AS cnt
FROM jams j
WHERE j.published_at >= %s AND j.published_at < %s
  AND j.street = ANY(%s)
  AND NULLIF(TRIM(j.street), '') IS NOT NULL
GROUP BY j.street
ORDER BY cnt DESC, j.street ASC
LIMIT %s;
"""

# ALERTS: top-N streets in interval (drop NULL/empty streets)
QUERY_TOP_STREETS_ALERTS_BASE = """
SELECT a.street, COUNT(*)::BIGINT AS cnt
FROM alerts a
WHERE a.published_at >= %s AND a.published_at < %s
  AND NULLIF(TRIM(a.street), '') IS NOT NULL
GROUP BY a.street
ORDER BY cnt DESC, a.street ASC
LIMIT %s;
"""

# ALERTS with explicit streets allowlist
QUERY_TOP_STREETS_ALERTS_WITH_STREETS = """
SELECT a.street, COUNT(*)::BIGINT AS cnt
FROM alerts a
WHERE a.published_at >= %s AND a.published_at < %s
  AND a.street = ANY(%s)
  AND NULLIF(TRIM(a.street), '') IS NOT NULL
GROUP BY a.street
ORDER BY cnt DESC, a.street ASC
LIMIT %s;
"""