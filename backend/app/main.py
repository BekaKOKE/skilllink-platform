from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

# Все модели должны быть импортированы ДО вызова create_all
import backend.app.db.models  # noqa: F401
from backend.app.api.v1.AuthRouter import router as auth_router
from backend.app.api.v1.CatalogRouter import router as catalog_router
from backend.app.api.v1.OrderRouter import router as order_router
from backend.app.api.v1.SpecialistRouter import router as specialist_router
from backend.app.api.v1.UserRouter import router as user_router
from backend.app.core.Redis import redis_client
from backend.app.db.session import engine
from backend.app.exceptions.NotFoundException import NotFoundException
from backend.app.exceptions.ValidationException import ValidationException


# -------------------------
# Lifespan FastAPI
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        await redis_client.ping()
        print("Redis connected ✅")
    except Exception as e:
        print(f"Couldn't connect to Redis ❌: {e}")

    yield

    await engine.dispose()
    await redis_client.aclose()


# -------------------------
# FASTAPI
# -------------------------
app = FastAPI(
    title="SkillLink API",
    description="Platform connecting clients with specialists",
    version="1.0.0",
    lifespan=lifespan
)

# -------------------------
# EXCEPTION HANDLERS
# -------------------------
@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail}
    )


@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors}
    )


# -------------------------
# ROUTERS
# -------------------------
app.include_router(auth_router,           prefix="/api/v1")
app.include_router(user_router,           prefix="/api/v1")
app.include_router(specialist_router,     prefix="/api/v1")
app.include_router(order_router,          prefix="/api/v1")
app.include_router(catalog_router,        prefix="/api/v1")


# -------------------------
# Health Check
# -------------------------
@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": "SkillLink API"}