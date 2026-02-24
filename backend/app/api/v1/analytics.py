from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel

from backend.app.core.dependencies import get_db, require_role
from backend.app.db.models.enums import UserRole, EventStatus
from backend.app.db.models.h3_zone_stats import H3ZoneStats
from backend.app.db.models.event_queue import EventQueue
from backend.app.db.models.specialist import Specialist
from backend.app.services.h3_service import H3Service

router = APIRouter()


# =========================================================
# Schemas
# =========================================================

class H3ZoneResponse(BaseModel):
    h3_index: str
    h3_resolution: int
    total_orders: int
    completed_orders: int
    avg_price: float
    active_specialists: int

    class Config:
        from_attributes = True


class EventQueueResponse(BaseModel):
    id: str
    event_type: str
    status: str
    payload: dict
    created_at: str
    processed_at: Optional[str] = None

    class Config:
        from_attributes = True


class H3NearbyStatsResponse(BaseModel):
    center_h3: str
    zones: List[H3ZoneResponse]
    total_orders_in_area: int
    total_specialists_in_area: int
    avg_price_in_area: float


# =========================================================
# H3 Zone Stats — агрегация
# =========================================================

@router.get("/h3/stats", response_model=List[H3ZoneResponse])
def get_h3_zone_stats(
    limit: int = Query(50, le=200),
    min_orders: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Агрегированная статистика по H3 зонам.
    Показывает количество заказов, среднюю цену и активных специалистов
    по каждой гексагональной ячейке.
    """
    query = db.query(H3ZoneStats)

    if min_orders > 0:
        query = query.filter(H3ZoneStats.total_orders >= min_orders)

    return (
        query
        .order_by(H3ZoneStats.total_orders.desc())
        .limit(limit)
        .all()
    )


@router.get("/h3/nearby-stats", response_model=H3NearbyStatsResponse)
def get_h3_nearby_stats(
    lat: float = Query(..., description="Широта центральной точки"),
    lon: float = Query(..., description="Долгота центральной точки"),
    radius: int = Query(1, ge=1, le=5, description="k-ring радиус"),
    db: Session = Depends(get_db),
):
    """
    Агрегированная статистика по H3 зонам вокруг заданной точки.
    Демонстрирует H3 query + filter + aggregation одновременно:
    - query: конвертация координат в H3 индекс
    - filter: выборка зон по k-ring соседям
    - aggregation: суммирование метрик по всем зонам в радиусе
    """
    # H3 query: конвертируем координаты в H3
    center_h3 = H3Service.geo_to_h3(lat, lon)

    # H3 filter: получаем все соседние ячейки
    neighbor_cells = H3Service.get_neighbors(center_h3, radius)

    # H3 aggregation: собираем статистику по всем ячейкам в радиусе
    zones = (
        db.query(H3ZoneStats)
        .filter(H3ZoneStats.h3_index.in_(neighbor_cells))
        .all()
    )

    # Считаем специалистов в зоне
    specialists_count = (
        db.query(func.count(Specialist.id))
        .filter(Specialist.h3_index.in_(neighbor_cells))
        .filter(Specialist.is_verified == True)
        .scalar()
    )

    total_orders = sum(z.total_orders for z in zones)
    avg_price = (
        sum(z.avg_price * z.total_orders for z in zones) / total_orders
        if total_orders > 0 else 0.0
    )

    return H3NearbyStatsResponse(
        center_h3=center_h3,
        zones=zones,
        total_orders_in_area=total_orders,
        total_specialists_in_area=specialists_count or 0,
        avg_price_in_area=round(avg_price, 2),
    )


@router.get("/h3/zone/{h3_index}", response_model=H3ZoneResponse)
def get_zone_by_index(
    h3_index: str,
    db: Session = Depends(get_db),
):
    """Получить статистику конкретной H3 ячейки по её индексу."""
    if not H3Service.validate_h3(h3_index):
        raise HTTPException(status_code=400, detail="Invalid H3 index")

    zone = db.get(H3ZoneStats, h3_index)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found — no orders in this cell yet")

    return zone


# =========================================================
# Event Queue — просмотр для демо
# =========================================================

@router.get("/events", response_model=List[dict])
def get_events(
    limit: int = Query(20, le=100),
    status: Optional[str] = Query(None, description="pending | processing | done | failed"),
    db: Session = Depends(get_db),
    _=Depends(require_role([UserRole.admin, UserRole.regulator])),
):
    """
    Просмотр очереди событий (event-driven log).
    Показывает все события: ORDER_CREATED и их статус обработки.
    """
    query = db.query(EventQueue)

    if status:
        try:
            status_enum = EventStatus(status)
            query = query.filter(EventQueue.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    events = query.order_by(EventQueue.created_at.desc()).limit(limit).all()

    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "status": e.status.value,
            "payload": e.payload,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "processed_at": e.processed_at.isoformat() if e.processed_at else None,
        }
        for e in events
    ]