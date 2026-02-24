import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.v1 import auth, users, specialists, orders, audit, analytics
from backend.app.db.session import SessionLocal
from backend.app.services.event_worker import EventWorker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("gig-platform")


async def event_loop_task():
    """Фоновый обработчик событий. Запускается каждые 5 секунд."""
    while True:
        db = SessionLocal()
        try:
            EventWorker.process_events(db)
        except Exception as e:
            logger.error(f"Event worker error: {e}")
        finally:
            db.close()
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Gig Platform API...")
    task = asyncio.create_task(event_loop_task())
    yield
    logger.info("Shutting down Gig Platform API...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Gig Platform API",
    description="H3-powered gig economy platform with RBAC, event-driven analytics, and audit logging.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,        prefix="/api/v1/auth",        tags=["Auth"])
app.include_router(users.router,       prefix="/api/v1/users",       tags=["Users"])
app.include_router(specialists.router, prefix="/api/v1/specialists", tags=["Specialists"])
app.include_router(orders.router,      prefix="/api/v1/orders",      tags=["Orders"])
app.include_router(audit.router,       prefix="/api/v1/audit",       tags=["Audit"])
app.include_router(analytics.router,   prefix="/api/v1/analytics",   tags=["Analytics & H3"])


@app.get("/", tags=["System"])
def root():
    return {"service": "Gig Platform API", "status": "running", "version": "1.0.0"}


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )