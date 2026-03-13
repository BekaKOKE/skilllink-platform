import uuid
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_client,
    require_any
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.message import Message
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.MessageSchema import MessageCreate
from backend.app.services.AuditService import AuditService
from backend.app.services.MessageService import MessageService

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)

# ─────────────────────────────────────────
# SEND MESSAGE
# ─────────────────────────────────────────

@router.post("/order/{order_id}")
async def send_message(
    order_id: uuid.UUID,
    data: MessageCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):
    message = await MessageService.create(
        session,
        order_id,
        current_user.id,
        data
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CREATE_MESSAGE,
        detail=f"Message sent in order {order_id}",
        ip_address=request.client.host
    )

    return message


# ─────────────────────────────────────────
# GET MESSAGES FOR ORDER
# ─────────────────────────────────────────

@router.get("/order/{order_id}", response_model=List[Message])
async def get_order_messages(
    order_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):
    messages = await MessageService.get_by_order_id(
        session,
        order_id,
        current_user.id
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.GET_ORDER_MESSAGES,
        detail=f"Requested messages for order {order_id}",
        ip_address=request.client.host
    )

    return messages