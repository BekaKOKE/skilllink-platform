from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.db.models.event_queue import EventQueue
from backend.app.db.models.enums import EventStatus
from backend.app.db.models.h3_zone_stats import H3ZoneStats


class EventWorker:

    @staticmethod
    def process_events(db: Session):

        events = (
            db.query(EventQueue)
            .filter(EventQueue.status == EventStatus.pending)
            .limit(20)
            .all()
        )

        for event in events:
            try:
                event.status = EventStatus.processing
                db.commit()

                if event.event_type == "ORDER_CREATED":
                    EventWorker.handle_order_created(db, event.payload)

                event.status = EventStatus.done
                event.processed_at = datetime.utcnow()
                db.commit()

            except Exception:
                event.status = EventStatus.failed
                db.commit()

    @staticmethod
    def handle_order_created(db: Session, payload: dict):

        h3_index = payload.get("h3_index")
        price = payload.get("price") or 0

        zone = db.get(H3ZoneStats, h3_index)

        if not zone:
            zone = H3ZoneStats(h3_index=h3_index)
            db.add(zone)
            db.commit()

        zone.total_orders += 1

        # обновление среднего
        zone.avg_price = (
            (zone.avg_price * (zone.total_orders - 1) + price)
            / zone.total_orders
        )

        db.commit()