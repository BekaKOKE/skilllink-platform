import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.db.session import AsyncSessionFactory
from backend.app.db.models.enums import LogType, ServiceType
from backend.app.services.a.AuditService import AuditService
from backend.app.core.Security import decode_token


def _classify(status_code: int) -> LogType:
    if status_code >= 500:
        return LogType.ERROR
    if status_code >= 400:
        return LogType.DEBUG
    return LogType.INFO


def _detect_service(path: str) -> ServiceType:
    if "/auth" in path:
        return ServiceType.AUTH
    if "/specialists" in path:
        return ServiceType.SPECIALIST
    if "/orders" in path:
        return ServiceType.ORDER
    if "/users" in path:
        return ServiceType.USER
    if "/catalog" in path:
        return ServiceType.CATALOG
    if "/requests" in path:
        return ServiceType.REQUEST
    return ServiceType.HTTP


def _extract_user_id(request: Request) -> uuid.UUID | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ")
    payload = decode_token(token)
    if not payload:
        return None
    try:
        return uuid.UUID(payload.get("sub"))
    except Exception:
        return None


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        user_id = _extract_user_id(request)

        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (
            request.client.host if request.client else "unknown"
        )
        client_port = request.client.port if request.client else 0
        method = request.method
        url = request.url.path
        if request.url.query:
            url += f"?{request.url.query}"

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            detail = f"{client_ip}:{client_port} - {method} - {url} - 500 - {elapsed_ms:.2f}ms"
            async with AsyncSessionFactory() as session:
                await AuditService.log(
                    session=session,
                    log_type=LogType.ERROR,
                    service=_detect_service(url),
                    user_id=user_id,
                    detail=detail,
                )
                await session.commit()
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        detail = f"{client_ip}:{client_port} - {method} - {url} - {status_code} - {elapsed_ms:.2f}ms"

        async with AsyncSessionFactory() as session:
            await AuditService.log(
                session=session,
                log_type=_classify(status_code),
                service=_detect_service(url),
                user_id=user_id,
                detail=detail,
            )
            await session.commit()

        return response