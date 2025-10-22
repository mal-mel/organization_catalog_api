from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Activity name cannot be empty')
        return v.strip()

    @field_validator('parent_id')
    @classmethod
    def validate_parent_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('parent_id must be positive')
        return v


class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Activity name cannot be empty')
        return v.strip() if v else v

    @field_validator('parent_id')
    @classmethod
    def validate_parent_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('parent_id must be positive')
        return v


class ActivityInDB(ActivityBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ActivitySimple(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class ActivityTree(ActivitySimple):
    children: List['ActivityTree'] = []
    parent_id: Optional[int] = None


class ActivityDetail(ActivitySimple):
    parent_id: Optional[int] = None
    children: List['ActivitySimple'] = []
    organizations_count: int = 0


ActivityTree.model_rebuild()
ActivityDetail.model_rebuild()