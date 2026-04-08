import logging
from datetime import datetime, timezone, timedelta

import psycopg2

from backend.app.tasks.celery_app import celery_app
from backend.app.core.config import settings
from backend.app.db.models.enums import OrderStatus

logger = logging.getLogger("skilllink.tasks")


@celery_app.task(name="tasks.cancel_expired_orders")
def cancel_expired_orders():
    threshold = datetime.now(timezone.utc) - timedelta(seconds=30)

    try:
        conn = psycopg2.connect(settings.DATABASE_URL_SYNC)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE orders
                    SET status    = %s,
                        is_active = %s
                    WHERE status = %s
                      AND created_at < %s RETURNING id
                    """,
                    (OrderStatus.cancelled.value, False, OrderStatus.open.value, threshold)
                )
                cancelled = cur.fetchall()

        conn.close()
        logger.info(f"[ORDERS] Cancelled {len(cancelled)} expired orders.")

    except Exception as exc:
        logger.error(f"[ORDERS] Failed to cancel expired orders: {exc}")
        raise