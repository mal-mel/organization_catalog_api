from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.schemas.activity import ActivitySimple

class PhoneNumberBase(BaseModel):
    number: str

class PhoneNumberCreate(PhoneNumberBase):
    pass

class PhoneNumber(PhoneNumberBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class OrganizationBase(BaseModel):
    name: str
    building_id: int

class OrganizationCreate(OrganizationBase):
    phone_numbers: List[PhoneNumberCreate] = []
    activity_ids: List[int] = []

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    building_id: Optional[int] = None
    phone_numbers: Optional[List[PhoneNumberCreate]] = None
    activity_ids: Optional[List[int]] = None

class OrganizationInDB(OrganizationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class OrganizationSimple(OrganizationInDB):
    phone_numbers: List[PhoneNumber] = []
    activities: List[ActivitySimple] = []

class OrganizationDetail(OrganizationSimple):
    activities: List[ActivitySimple] = []
