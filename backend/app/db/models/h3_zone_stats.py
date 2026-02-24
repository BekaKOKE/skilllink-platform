from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from backend.app.db.base import Base


class H3ZoneStats(Base):
    __tablename__ = "h3_zone_stats"

    h3_index: Mapped[str] = mapped_column(String(32), primary_key=True)

    h3_resolution: Mapped[int] = mapped_column(Integer, default=7)

    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0)

    avg_price: Mapped[float] = mapped_column(Float, default=0.0)
    active_specialists: Mapped[int] = mapped_column(Integer, default=0)

    last_updated: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )