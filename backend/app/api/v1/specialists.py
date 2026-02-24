from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.core.dependencies import get_db, get_current_user, require_role
from backend.app.db.models.enums import UserRole
from backend.app.db.models.specialist import Specialist
from backend.app.schemas.specialist import SpecialistCreate, SpecialistUpdate, SpecialistResponse
from backend.app.services.search_service import SearchService
from backend.app.services.specialist_service import SpecialistService
from backend.app.services.audit_service import AuditService

router = APIRouter()


@router.get("/nearby")
def get_specialists_nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: int = Query(1, ge=1, le=5),
    db: Session = Depends(get_db),
):
    """Найти специалистов рядом по координатам."""
    return SearchService.find_specialists_nearby(db, lat, lon, radius)


@router.post("/", response_model=SpecialistResponse)
def create_specialist(
    data: SpecialistCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_role([UserRole.specialist])),
):
    """Создать профиль специалиста (только для роли specialist)."""
    existing = db.query(Specialist).filter(Specialist.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Specialist profile already exists")

    specialist = SpecialistService.create_specialist(db, current_user.id, data)

    AuditService.log_action(
        db=db,
        action="SPECIALIST_CREATED",
        request=request,
        user=current_user,
        resource="specialists",
        resource_id=specialist.id,
    )

    return specialist


@router.get("/{specialist_id}", response_model=SpecialistResponse)
def get_specialist(specialist_id: UUID, db: Session = Depends(get_db)):
    """Получить профиль специалиста по ID."""
    specialist = db.query(Specialist).filter(Specialist.id == specialist_id).first()
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    return specialist


@router.patch("/{specialist_id}/verify", response_model=SpecialistResponse)
def verify_specialist(
    specialist_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_role([UserRole.admin])),
):
    """Верифицировать специалиста (только admin). После этого он появляется в поиске."""
    specialist = db.query(Specialist).filter(Specialist.id == specialist_id).first()
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    if specialist.is_verified:
        raise HTTPException(status_code=400, detail="Specialist is already verified")

    specialist.is_verified = True
    db.commit()
    db.refresh(specialist)

    AuditService.log_action(
        db=db,
        action="SPECIALIST_VERIFIED",
        request=request,
        user=current_user,
        resource="specialists",
        resource_id=specialist_id,
    )

    return specialist


@router.patch("/{specialist_id}", response_model=SpecialistResponse)
def update_specialist(
    specialist_id: UUID,
    data: SpecialistUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Обновить профиль специалиста (сам специалист или admin)."""
    specialist = db.query(Specialist).filter(Specialist.id == specialist_id).first()
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    if current_user.role != UserRole.admin and specialist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = data.model_dump(exclude_unset=True)

    # Если обновились координаты — пересчитать h3_index
    if "lat" in update_data or "lon" in update_data:
        from backend.app.services.h3_service import H3Service
        lat = update_data.get("lat", specialist.lat)
        lon = update_data.get("lon", specialist.lon)
        update_data["h3_index"] = H3Service.geo_to_h3(lat, lon)

    for field, value in update_data.items():
        setattr(specialist, field, value)

    db.commit()
    db.refresh(specialist)

    AuditService.log_action(
        db=db,
        action="SPECIALIST_UPDATED",
        request=request,
        user=current_user,
        resource="specialists",
        resource_id=specialist_id,
    )

    return specialist