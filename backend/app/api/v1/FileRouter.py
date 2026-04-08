from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response

from backend.app.core.dependencies import (
    require_any
)
import base64
from fastapi import UploadFile, File

from backend.app.db.session import get_session
from backend.app.services.FileService import FileService
from backend.app.services.SpecialistService import SpecialistService
from backend.app.tasks.image_tasks import compress_and_store_image
from backend.app.core.config import settings
from backend.app.db.models.user import User

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

@router.post("/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files accepted.")

    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Max size 10MB.")

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist profile not found.")

    compress_and_store_image.delay(
        specialist_id=str(specialist.id),
        image_b64=base64.b64encode(raw).decode(),
        db_url=settings.DATABASE_URL_SYNC,
    )

    return {
        "message": "Image queued for compression.",
        "original_size_bytes": len(raw),
    }

@router.get("/get/avatar")
async def get_avatar(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any),
):
    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if not specialist:
        raise HTTPException(404, "Specialist not found")

    row = await FileService.get_avatar(session, specialist.id)

    if not row:
        raise HTTPException(status_code=404, detail="Avatar not found")

    image_data, content_type = row

    return Response(
        content=image_data,
        media_type=content_type or "image/jpeg"
    )