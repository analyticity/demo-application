from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from logging_config import setup_logging
from middleware.request_logging import request_logging_middleware

from routers import homepage_endpoints, alerts_endpoints, jams_endpoints, plot_endpoints, health_endpoints,\
    dashboard_endpoints

logger = setup_logging()

app = FastAPI()

app.include_router(homepage_endpoints.router)
app.include_router(alerts_endpoints.router)
app.include_router(jams_endpoints.router)
app.include_router(plot_endpoints.router)
app.include_router(health_endpoints.router)
app.include_router(dashboard_endpoints.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.middleware("http")
async def _request_logger(request, call_next):
    return await request_logging_middleware(request, call_next)
