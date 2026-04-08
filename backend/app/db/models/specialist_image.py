import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field


class SpecialistImage(SQLModel, table=True):
    __tablename__ = "specialist_images"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    specialist_id: uuid.UUID = Field(foreign_key="specialist.id")
    image_data: bytes = Field(sa_column_kwargs={"nullable": True})
    content_type: str = Field(default="image/jpeg")
    original_size_bytes: int
    compressed_size_bytes: int
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False
    )