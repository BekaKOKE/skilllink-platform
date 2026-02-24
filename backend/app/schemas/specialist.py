from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class SpecialistCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., min_length=2, max_length=100)
    lat: float
    lon: float
    license_number: Optional[str] = None

class SpecialistUpdate(BaseModel):
    full_name: Optional[str] = None
    category: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    license_number: Optional[str] = None
    is_verified: Optional[bool] = None

class SpecialistResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    category: str
    lat: float
    lon: float
    h3_index: str
    is_verified: bool
    rating: float
    total_orders: int

    class Config:
        from_attributes = True