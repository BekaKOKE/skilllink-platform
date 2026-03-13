import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class SpecialistBase(BaseModel):
    pass

class SpecialistCreate(SpecialistBase):
    lat: float
    lon: float

class SpecialistUpdate(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    is_active: Optional[bool] = None

class SpecialistDto(SpecialistBase):
    id: uuid.UUID
    user_id: uuid.UUID
    h3_index: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    model_config = {"from_attributes": True}