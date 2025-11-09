from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional

road_type_mapping = {
    1: "Streets",
    2: "Primary Street",
    3: "Freeways",
    4: "Ramps",
    5: "Trails",
    6: "Primary",
    7: "Secondary",
    8: "4X4 Trails",
    14: "4X4 Trails",  # Multiple values for 4X4 Trails
    15: "Ferry crossing",
    9: "Walkway",
    10: "Pedestrian",
    11: "Exit",
    16: "Stairway",
    17: "Private road",
    18: "Railroads",
    19: "Runway/Taxiway",
    20: "Parking lot road",
    21: "Service road",
}

class Location(BaseModel):
    """
    Represents a geographic coordinate with x and y values.
    Typically used for longitude (x) and latitude (y) coordinates.
    """
    x: float = Field(..., description="Longitude coordinate")
    y: float = Field(..., description="Latitude coordinate")

class WazeFileAttributes(BaseModel):
    country: str
    city: str
    reportRating: int
    reportByMunicipalityUser: str
    confidence: int
    reliability: int  # 0 - 10
    type: str
    uuid: str
    roadType: Optional[int]
    roadTypeName: str = "Unknown"
    magvar: int
    subtype: Optional[str]
    street: Optional[str]
    reportDescription: Optional[str]
    location: Location
    pubMillis: datetime
    finished: bool
    intersecting_street_indexes: list[int]

    @field_validator("pubMillis", mode="before")
    def transform_pubMillis(cls, value):
        return datetime.fromtimestamp(value / 1000)

    @model_validator(mode="after")
    def set_road_type_name(self):
        road_type_name = road_type_mapping.get(self.roadType, "Unknown")
        self.roadTypeName = road_type_name
        return self
