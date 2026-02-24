from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.db.models.event_queue import EventQueue
from backend.app.db.models.enums import EventStatus


class EventService:

    @staticmethod
    def publish_event(db: Session, event_type: str, payload: dict):
        event = EventQueue(
            event_type=event_type,
            payload=payload,
            status=EventStatus.pending
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event