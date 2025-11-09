from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional

T = TypeVar("T")


# Model for the Spatial Reference (Wkid)
class SpatialReference(BaseModel):
    wkid: int
    latestWkid: int


# Model for Geometry (longitude and latitude)
class Geometry(BaseModel):
    x: float  # Longitude
    y: float  # Latitude


# Model for each Feature that combines attributes and geometry
class Feature(BaseModel, Generic[T]):
    attributes: T
    geometry: Geometry


# Main ArcGIS response model
class ArcGISResponse(BaseModel, Generic[T]):
    hasZ: Optional[bool] = None
    hasM: Optional[bool] = None
    features: List[Feature[T]]
    exceededTransferLimit: Optional[bool] = None
    globalIdFieldName: Optional[str] = None
    objectIdFieldName: Optional[str] = None
    spatialReference: Optional[SpatialReference] = None
    geometryType: Optional[str] = None
