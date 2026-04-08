import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_specialist
)
from backend.app.db.models.enums import LogType, ServiceType
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.CatalogSchema import CatalogCreate, CatalogUpdate, CatalogFilter, CatalogDto
from backend.app.services.a.CatalogService import CatalogService
from backend.app.services.SpecialistService import SpecialistService

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"]
)

# ─────────────────────────────────────────
# CREATE CATALOG ITEM
# ─────────────────────────────────────────

@router.post("/create", response_model=CatalogDto)
async def create_catalog_item(
    data: CatalogCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if not specialist:
        raise HTTPException(404, "Specialist profile not found")

    item = await CatalogService.create(
        session,
        specialist.id,
        data
    )

    return item

# ─────────────────────────────────────────
# GET SPECIALIST CATALOG
# ─────────────────────────────────────────

@router.get("/get/catalog/{specialist_id}", response_model=list[CatalogDto])
async def get_specialist_catalog(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    filters: CatalogFilter = Depends(),
    current_user: User = Depends(require_specialist)
):

    items = await CatalogService.get_by_specialist_id(
        session,
        specialist_id,
        filters
    )

    return items


# ─────────────────────────────────────────
# UPDATE CATALOG ITEM
# ─────────────────────────────────────────

@router.put("/update/{catalog_id}", response_model=CatalogDto)
async def update_catalog_item(
    catalog_id: uuid.UUID,
    data: CatalogUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    item = await CatalogService.get_all(session, CatalogFilter())

    item = next((i for i in item if i.id == catalog_id), None)

    if not item:
        raise HTTPException(404, f"Catalog item {catalog_id} not found")

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if item.specialist_id != specialist.id:
        raise HTTPException(403, "Not allowed to update catalog item")

    updated = await CatalogService.update(session, item, data)

    return updated


# ─────────────────────────────────────────
# DELETE CATALOG ITEM
# ─────────────────────────────────────────

@router.delete("/delete/{catalog_id}", response_model=dict[str, str])
async def delete_catalog_item(
    catalog_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    items = await CatalogService.get_all(session, CatalogFilter())

    item = next((i for i in items if i.id == catalog_id), None)

    if not item:
        raise HTTPException(404, f"Catalog item not found")

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if item.specialist_id != specialist.id:
        raise HTTPException(403, "Not allowed to delete catalog item")

    await CatalogService.delete(session, item)

    return {"message": "Catalog item deleted"}