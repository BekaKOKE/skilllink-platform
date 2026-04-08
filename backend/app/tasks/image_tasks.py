import base64
import io
import logging

from backend.app.tasks.celery_app import celery_app

logger = logging.getLogger("skilllink.tasks")

MAX_WIDTH = 1024
JPEG_QUALITY = 60


def _compress(raw_bytes: bytes) -> bytes:
    from PIL import Image

    img = Image.open(io.BytesIO(raw_bytes))
    img = img.convert("RGB")

    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize((MAX_WIDTH, int(img.height * ratio)))

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return out.getvalue()


@celery_app.task(name="tasks.compress_and_store_image", bind=True, max_retries=3, default_retry_delay=15)
def compress_and_store_image(self, specialist_id: str, image_b64: str, db_url: str):
    import psycopg2

    try:
        raw_bytes = base64.b64decode(image_b64)
        original_kb = len(raw_bytes) / 1024

        compressed = _compress(raw_bytes)
        compressed_kb = len(compressed) / 1024

        logger.info(
            f"[IMAGE] specialist={specialist_id} | "
            f"before={original_kb:.1f} KB | "
            f"after={compressed_kb:.1f} KB | "
            f"ratio={compressed_kb / original_kb:.1%}"
        )

        conn = psycopg2.connect(db_url)
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO specialist_images
                    (id, specialist_id, image_data, content_type,
                     original_size_bytes, compressed_size_bytes, uploaded_at)
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, now())
                    """,
                    (
                        specialist_id,
                        psycopg2.Binary(compressed),
                        "image/jpeg",
                        len(raw_bytes),
                        len(compressed),
                    ),
                )
        conn.close()
        logger.info(f"[IMAGE] Stored compressed image for specialist={specialist_id}")

    except Exception as exc:
        logger.error(f"[IMAGE] Failed for specialist={specialist_id}: {exc}")
        raise self.retry(exc=exc)