import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_client,
    require_specialist,
    require_any
)
from backend.app.db.models.enums import ServiceType, OrderStatus, LogType
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.OrderRequestsSchema import OrderRequestCreate
from backend.app.schemas.OrderSchema import OrderCreate, OrderUpdate, OrderDto
from backend.app.services.OrderService import OrderService
from backend.app.services.OrderRequestsService import OrderRequestsService
from backend.app.services.SpecialistService import SpecialistService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# ─────────────────────────────────────────
# CREATE ORDER
# ─────────────────────────────────────────

@router.post("/create", response_model=OrderDto)
async def create_order(
    data: OrderCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):

    order = await OrderService.create(
        session,
        current_user.id,
        data
    )

    return order


# ─────────────────────────────────────────
# GET ORDER BY ID
# ─────────────────────────────────────────

@router.get("/get/{order_id}", response_model=OrderDto)
async def get_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")
    return order


# ─────────────────────────────────────────
# USER ORDERS
# ─────────────────────────────────────────

@router.get("/my", response_model=list[OrderDto])
async def get_my_orders(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    orders =  await OrderService.get_user_orders(session, current_user.id)

    return orders

# ─────────────────────────────────────────
# ACTIVE ORDERS
# ─────────────────────────────────────────

@router.get("/active", response_model=list[OrderDto])
async def get_active_orders(
    request: Request,
    session: AsyncSession = Depends(get_session),
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    current_user: User = Depends(require_specialist)
):
    orders =  await OrderService.get_active_orders(session, limit, offset)

    return orders


# ─────────────────────────────────────────
# SPECIALIST ORDERS
# ─────────────────────────────────────────

@router.get("/specialist/my", response_model=list[OrderDto])
async def get_specialist_orders(
    request: Request,
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

@router.put("/update/{order_id}", response_model=OrderDto)
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

    if order.user_id != current_user.id:
        raise HTTPException(403, "Not allowed to update order")

    result = await OrderService.update(session, order, data)

    return result


# ─────────────────────────────────────────
# TAKE ORDER (specialist)
# ─────────────────────────────────────────

@router.post("/take/{order_id}", response_model=dict[str, str])
async def take_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if not specialist:
        raise HTTPException(404, "Specialist profile not found")

    order = await OrderService.get_by_id(session, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != OrderStatus.open:
        raise HTTPException(400, "Order is not available")
    if order.user_id == current_user.id:
        raise HTTPException(400, "Cannot take your own order")

    data = OrderRequestCreate(
        user_id=order.user_id,
        specialist_id=specialist.id,
        order_id = order.id
    )

    await OrderRequestsService.try_to_take_order(session,data)

    return {"message": "Thank You for the interest. Please Wait the approval"}


# ─────────────────────────────────────────
# COMPLETE ORDER
# ─────────────────────────────────────────

@router.post("/complete/{order_id}", response_model=OrderDto)
async def complete_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")
    if order.user_id == current_user.id:
        raise HTTPException(404, "Not allowed to delete order")

    result = await OrderService.complete_order(
        session,
        order,
        current_user.id
    )

    return result


# ─────────────────────────────────────────
# CANCEL ORDER
# ─────────────────────────────────────────

@router.post("/cancel/{order_id}", response_model=OrderDto)
async def cancel_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    if order.user_id == current_user.id:
        raise HTTPException(404, "Not allowed to delete order")

    result = await OrderService.cancel_order(
        session,
        order,
        current_user.id
    )
    return result


# ─────────────────────────────────────────
# DELETE ORDER
# ─────────────────────────────────────────

@router.delete("/delete/{order_id}", response_model=dict[str, str])
async def delete_order(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    order = await OrderService.get_by_id(session, order_id)

    if not order:
        raise HTTPException(404, "Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(403, "Not allowed to delete order")

    await OrderService.delete(session, order)

    return {"message": "Order deleted"}