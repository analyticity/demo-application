import os
import logging
from logging.config import dictConfig

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "plain").lower()  # "plain" | "json"


def _json_formatter():
    return {
        "format": (
            '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"msg":"%(message)s","request_id":"%(request_id)s","path":"%(path)s",'
            '"method":"%(method)s","status":"%(status)s","duration_ms":"%(duration_ms)s"}'
        ),
        "datefmt": "%Y-%m-%dT%H:%M:%S%z",
    }


def _plain_formatter():
    return {
        "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }


class RequestContextFilter(logging.Filter):
    
    def filter(self, record: logging.LogRecord) -> bool:
        for key in ("request_id", "path", "method", "status", "duration_ms"):
            if not hasattr(record, key):
                setattr(record, key, "")
        return True


def setup_logging() -> logging.Logger:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": _plain_formatter(),
            "json": _json_formatter(),
        },
        "filters": {
            "requestctx": {"()": RequestContextFilter},
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "json" if LOG_FORMAT == "json" else "plain",
                "filters": ["requestctx"],
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
        },
        "root": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
        },
    })
    return logging.getLogger("app")
