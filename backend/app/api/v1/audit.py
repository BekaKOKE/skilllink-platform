from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db, require_role
from backend.app.db.models.enums import UserRole
from backend.app.db.models.audit_log import AuditLog

router = APIRouter()


@router.get("/")
def get_audit_logs(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user=Depends(require_role([UserRole.regulator, UserRole.admin]))
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )