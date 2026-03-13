import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_client
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.CommentSchema import CommentCreate, CommentFilter, CommentDto
from backend.app.services.AuditService import AuditService
from backend.app.services.CommentService import CommentService

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

# ─────────────────────────────────────────
# CREATE COMMENT
# ─────────────────────────────────────────

@router.post("/", response_model=CommentDto)
async def create_comment(
    data: CommentCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    comment = await CommentService.create(
        session,
        current_user.id,
        data
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CREATE_COMMENT,
        detail=f"Comment created {comment.id}",
        ip_address=request.client.host
    )

    return comment


# ─────────────────────────────────────────
# GET COMMENTS OF SPECIALIST
# ─────────────────────────────────────────

@router.get("/specialist/{specialist_id}", response_model=list[CommentDto])
async def get_specialist_comments(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    filters: CommentFilter = Depends()
):

    comments = await CommentService.get_by_id(
        session,
        specialist_id,
        filters
    )

    await AuditService.log(
        session=session,
        action=AuditAction.GET_SPECIALIST_COMMENTS,
        detail=f"Requested comments for specialist {specialist_id}",
        ip_address=request.client.host
    )

    return comments

# ─────────────────────────────────────────
# DELETE COMMENT
# ─────────────────────────────────────────

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    comments = await CommentService.get_all(session, CommentFilter())

    comment = next((c for c in comments if c.id == comment_id), None)

    if not comment:
        raise HTTPException(404, "Comment not found")

    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Not allowed")

    await CommentService.delete(session, comment)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.DELETE_COMMENT,
        detail=f"Deleted comment {comment_id}",
        ip_address=request.client.host
    )

    return {"message": "Comment deleted"}