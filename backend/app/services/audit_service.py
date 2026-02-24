from sqlalchemy.orm import Session
from fastapi import Request

from backend.app.db.models.audit_log import AuditLog


class AuditService:

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        request: Request,
        user=None,
        resource: str | None = None,
        resource_id=None,
        detail: str | None = None,
    ):
        ip = request.client.host if request.client else None

        log = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else None,
            action=action,
            resource=resource,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip,
        )

        db.add(log)
        db.commit()