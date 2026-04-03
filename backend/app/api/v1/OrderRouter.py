import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_client,
    require_specialist,
    require_any
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.OrderSchema import OrderCreate, OrderUpdate, OrderDto
from backend.app.services.AuditService import AuditService
from backend.app.services.OrderService import OrderService
from backend.app.services.SpecialistService import SpecialistService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# ─────────────────────────────────────────
# CREATE ORDER
# ─────────────────────────────────────────

@router.post("/", response_model=OrderDto)
async def create_order(
    data: OrderCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    order = await OrderService.create(
        session,
        current_user.id,
        data
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CREATE_ORDER,
        detail=f"Order created {order.id}",
        ip_address=request.client.host
    )

    return order


# ─────────────────────────────────────────
# GET ORDER BY ID
# ─────────────────────────────────────────

@router.get("/{order_id}", response_model=OrderDto)
async def get_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.GET_ORDER,
        detail=f"Requested order {order_id}",
        ip_address=request.client.host
    )

    return order


# ─────────────────────────────────────────
# USER ORDERS
# ─────────────────────────────────────────

@router.get("/my", response_model=list[OrderDto])
async def get_my_orders(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    orders =  await OrderService.get_user_orders(session, current_user.id)
    return orders

# ─────────────────────────────────────────
# ACTIVE ORDERS
# ─────────────────────────────────────────

@router.get("/active/list", response_model=list[OrderDto])
async def get_active_orders(
    session: AsyncSession = Depends(get_session),
    limit: Optional[int] = None,
    offset: Optional[int] = None
):

    return await OrderService.get_active_orders(session, limit, offset)


# ─────────────────────────────────────────
# SPECIALIST ORDERS
# ─────────────────────────────────────────

@router.get("/specialist/my", response_model=list[OrderDto])
async def get_specialist_orders(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if not specialist:
        raise HTTPException(404, "Specialist profile not found")

    return await OrderService.get_specialist_orders(session, specialist.id)


# ─────────────────────────────────────────
# UPDATE ORDER
# ─────────────────────────────────────────

@router.put("/{order_id}", response_model=OrderDto)
async def update_order(
    order_id: uuid.UUID,
    data: OrderUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Not allowed")

    result = await OrderService.update(session, order, data)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.UPDATE_ORDER,
        detail=f"Updated order {order_id}",
        ip_address=request.client.host
    )

    return result


# ─────────────────────────────────────────
# TAKE ORDER (specialist)
# ─────────────────────────────────────────

@router.post("/{order_id}/take", response_model=OrderDto)
async def take_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if not specialist:
        raise HTTPException(404, "Specialist profile not found")

    result = await OrderService.take_order(
        session,
        order_id,
        specialist.id
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.TAKE_ORDER,
        detail=f"Specialist took order {order_id}",
        ip_address=request.client.host
    )

    return result


# ─────────────────────────────────────────
# COMPLETE ORDER
# ─────────────────────────────────────────

@router.post("/{order_id}/complete", response_model=OrderDto)
async def complete_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    result = await OrderService.complete_order(
        session,
        order,
        current_user.id
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.COMPLETE_ORDER,
        detail=f"Completed order {order_id}",
        ip_address=request.client.host
    )

    return result


# ─────────────────────────────────────────
# CANCEL ORDER
# ─────────────────────────────────────────

@router.post("/{order_id}/cancel", response_model=OrderDto)
async def cancel_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    result = await OrderService.cancel_order(
        session,
        order,
        current_user.id
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CANCEL_ORDER,
        detail=f"Cancelled order {order_id}",
        ip_address=request.client.host
    )

    return result


# ─────────────────────────────────────────
# DELETE ORDER
# ─────────────────────────────────────────

@router.delete("/{order_id}")
async def delete_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    await OrderService.delete(session, order)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.DELETE_ORDER,
        detail=f"Admin deleted order {order_id}",
        ip_address=request.client.host
    )

    return {"message": "Order deleted"}