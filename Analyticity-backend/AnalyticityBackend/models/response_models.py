from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class Stats(BaseModel):
    jams: int = Field(..., description="Number of traffic jams")
    alerts: int = Field(..., description="Number of traffic alerts")
    speedKMH: float = Field(..., description="Average speed in kilometers per hour")
    delay: float = Field(..., description="Total delay in minutes (or -1 if unavailable)")
    level: float = Field(..., description="Traffic congestion level")
    length: float = Field(..., description="Total affected road length in kilometers")


class StatsResponse(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp of the data")
    stats: Stats = Field(..., description="Traffic statistics at the given time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "timestamp": "2025-04-12 02:00:00",
                "stats": {
                    "jams": 140,
                    "alerts": 158,
                    "speedKMH": 0.0,
                    "delay": -1.0,
                    "level": 5.0,
                    "length": 115.81
                }
            }
        }
    }


class LegacyPlotResponse(BaseModel):
    jams: List[int]
    alerts: List[int]
    speedKMH: List[float]
    delay: List[float]
    level: List[float]
    length: List[float]
    xaxis: List[int]


class TotalStatsResponse(BaseModel):
    data_jams: int
    data_alerts: int
    speedKMH: float
    delay: float
    level: float
    length: float
