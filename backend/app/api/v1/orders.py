from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.core.dependencies import get_db, get_current_user, require_role
from backend.app.db.models.enums import UserRole, OrderStatus
from backend.app.db.models.order import Order
from backend.app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse
from backend.app.services.order_service import OrderService
from backend.app.services.audit_service import AuditService

router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_role([UserRole.client])),
):
    """Создать заказ (только client)."""
    order = OrderService.create_order(db, user.id, data)

    AuditService.log_action(
        db=db,
        action="ORDER_CREATED",
        request=request,
        user=user,
        resource="orders",
        resource_id=order.id,
        detail=f"Service type: {order.service_type}",
    )

    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Получить заказ по ID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Доступ: клиент видит свои заказы, специалист — свои, admin/regulator — все
    if current_user.role not in (UserRole.admin, UserRole.regulator):
        if order.client_id != current_user.id and order.specialist_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Обновить статус заказа (специалист или admin)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Только специалист назначенный на заказ или admin
    if current_user.role != UserRole.admin and order.specialist_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    order.status = data.status
    db.commit()
    db.refresh(order)

    AuditService.log_action(
        db=db,
        action="ORDER_STATUS_UPDATED",
        request=request,
        user=current_user,
        resource="orders",
        resource_id=order_id,
        detail=f"New status: {data.status}",
    )

    return order