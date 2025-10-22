from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.organization import OrganizationSimple

class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float

class BuildingCreate(BuildingBase):
    pass

class BuildingUpdate(BaseModel):
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class BuildingInDB(BuildingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BuildingSimple(BuildingInDB):
    pass

class BuildingWithDistance(BuildingSimple):
    distance: Optional[float] = None

class BuildingDetail(BuildingSimple):
    organizations: List[OrganizationSimple] = []