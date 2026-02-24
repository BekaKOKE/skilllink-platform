from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from backend.app.db.models.enums import OrderStatus

class OrderCreate(BaseModel):
    specialist_id: UUID
    service_type: str = Field(..., min_length=2, max_length=100)
    lat: Optional[float] = None
    lon: Optional[float] = None
    price: Optional[float] = None
    description: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderResponse(BaseModel):
    id: UUID
    client_id: UUID
    specialist_id: UUID
    service_type: str
    status: OrderStatus
    lat: Optional[float]
    lon: Optional[float]
    h3_index: Optional[str]
    price: Optional[float]
    description: Optional[str]

    class Config:
        from_attributes = True