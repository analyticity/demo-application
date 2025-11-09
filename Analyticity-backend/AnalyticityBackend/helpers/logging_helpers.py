import time
import logging
import psycopg2

logger = logging.getLogger("app")


def request_extras(request, status="", duration_ms=""):
    req_id = getattr(request.state, "request_id", "unknown")
    return {
        "request_id": req_id,
        "path": request.url.path,
        "method": request.method,
        "status": status,
        "duration_ms": duration_ms,
    }


def safe_dsn_from_connection(conn: psycopg2.extensions.connection) -> str:
    dsn_params = conn.get_dsn_parameters() if hasattr(conn, "get_dsn_parameters") else {}
    host = dsn_params.get("host", "unknown")
    db = dsn_params.get("dbname", "unknown")
    user = dsn_params.get("user", "unknown")
    port = dsn_params.get("port", "5432")
    return f"postgresql://{user}@{host}:{port}/{db}"


class Stopwatch:

    def __init__(self) -> None:
        self._t = time.perf_counter()

    def ms(self) -> int:
        return int((time.perf_counter() - self._t) * 1000)
