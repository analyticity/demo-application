import time
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Callable
import logging

logger = logging.getLogger("app")


async def request_logging_middleware(request: Request, call_next: Callable):
    """
    - Create/loads request_id (X-Request-ID)
    - Log request
    - Add X-Request-ID to response
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()

    logger.info(
        f"Incoming request {request.method} {request.url.path}",
        extra={"request_id": request_id, "path": request.url.path, "method": request.method}
    )

    try:
        response = await call_next(request)
        status_code = getattr(response, "status_code", 0)
        duration_ms = int((time.perf_counter() - start) * 1000)

        logger.info(
            f"Handled {request.method} {request.url.path} -> {status_code} in {duration_ms} ms",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status": status_code,
                "duration_ms": duration_ms,
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response

    except Exception:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            f"Unhandled error for {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status": 500,
                "duration_ms": duration_ms,
            },
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
        )
