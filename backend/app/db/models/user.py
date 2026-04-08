from datetime import datetime, date, timezone
from typing import TYPE_CHECKING
from typing import Optional
import uuid

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship

from backend.app.db.models.enums import UserRole
if TYPE_CHECKING:
    from backend.app.db.models.address import Address
    from backend.app.db.models.specialist import Specialist
    from backend.app.db.models.orders import Order
    from backend.app.db.models.rate import Rate
    from backend.app.db.models.comment import Comment
    from backend.app.db.models.auditLog import AuditLog
    from backend.app.db.models.message import Message
    from backend.app.db.models.order_request import OrderRequest

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    role: UserRole = Field(default=UserRole.client)
    name: str
    surname: str
    birth_date: date
    phone: str = Field(unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False
    )

    # Relationships
    address: Optional["Address"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    specialist: Optional["Specialist"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    orders: list["Order"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    rates: list["Rate"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    comments: list["Comment"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    audit_logs: list["AuditLog"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    messages: list["Message"] = Relationship(back_populates="sender", sa_relationship_kwargs={"lazy": "selectin"})
    order_requests: list["OrderRequest"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})