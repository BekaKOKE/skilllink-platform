import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_specialist,
    require_any
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.CatalogSchema import CatalogCreate, CatalogUpdate, CatalogFilter
from backend.app.services.AuditService import AuditService
from backend.app.services.CatalogService import CatalogService
from backend.app.services.SpecialistService import SpecialistService

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"]
)

# ─────────────────────────────────────────
# CREATE CATALOG ITEM
# ─────────────────────────────────────────

@router.post("/")
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

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CREATE_CATALOG_ITEM,
        detail=f"Catalog item created {item.id}",
        ip_address=request.client.host
    )

    return item


# ─────────────────────────────────────────
# GET ALL CATALOG ITEMS
# ─────────────────────────────────────────

@router.get("/")
async def get_catalog(
    request: Request,
    session: AsyncSession = Depends(get_session),
    filters: CatalogFilter = Depends(),
    limit: Optional[int] = None,
    offset: Optional[int] = None
):

    items = await CatalogService.get_all(
        session,
        filters,
        limit,
        offset
    )

    await AuditService.log(
        session=session,
        action=AuditAction.GET_CATALOG,
        detail="Requested catalog list",
        ip_address=request.client.host
    )

    return items


# ─────────────────────────────────────────
# GET SPECIALIST CATALOG
# ─────────────────────────────────────────

@router.get("/specialist/{specialist_id}")
async def get_specialist_catalog(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    filters: CatalogFilter = Depends()
):

    items = await CatalogService.get_by_specialist_id(
        session,
        specialist_id,
        filters
    )

    await AuditService.log(
        session=session,
        action=AuditAction.GET_SPECIALIST_CATALOG,
        detail=f"Requested catalog of specialist {specialist_id}",
        ip_address=request.client.host
    )

    return items


# ─────────────────────────────────────────
# UPDATE CATALOG ITEM
# ─────────────────────────────────────────

@router.put("/{catalog_id}")
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
        raise HTTPException(404, "Catalog item not found")

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if item.specialist_id != specialist.id and current_user.role != "admin":
        raise HTTPException(403, "Not allowed")

    updated = await CatalogService.update(session, item, data)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.UPDATE_CATALOG_ITEM,
        detail=f"Updated catalog item {catalog_id}",
        ip_address=request.client.host
    )

    return updated


# ─────────────────────────────────────────
# DELETE CATALOG ITEM
# ─────────────────────────────────────────

@router.delete("/{catalog_id}")
async def delete_catalog_item(
    catalog_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    items = await CatalogService.get_all(session, CatalogFilter())

    item = next((i for i in items if i.id == catalog_id), None)

    if not item:
        raise HTTPException(404, "Catalog item not found")

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if item.specialist_id != specialist.id and current_user.role != "admin":
        raise HTTPException(403, "Not allowed")

    await CatalogService.delete(session, item)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.DELETE_CATALOG_ITEM,
        detail=f"Deleted catalog item {catalog_id}",
        ip_address=request.client.host
    )

    return {"message": "Catalog item deleted"}