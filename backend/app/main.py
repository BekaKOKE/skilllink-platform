from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Все модели должны быть импортированы ДО вызова create_all
import backend.app.db.models  # noqa: F401
from backend.app.api.v1.AuthRouter import router as auth_router
from backend.app.api.v1.CatalogRouter import router as catalog_router
from backend.app.api.v1.OrderRouter import router as order_router
from backend.app.api.v1.SpecialistRouter import router as specialist_router
from backend.app.api.v1.UserRouter import router as user_router
from backend.app.api.v1.RequestsRouter import router as request_router
from backend.app.api.v1.FileRouter import router as file_router
from backend.app.core.Redis import redis_client
from backend.app.db.session import engine
from backend.app.exceptions.NotFoundException import NotFoundException
from backend.app.exceptions.ValidationException import ValidationException
from backend.app.middleware.middleware import LoggingMiddleware
from backend.app.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.app.middleware.profiling_middleware import ProfilingMiddleware, get_latency_report


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
# MIDDLEWARE
# -------------------------

# 1a. CORS
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ProfilingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://skilllink.kz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1a. TrustedHost
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "skilllink.kz",
        "*.skilllink.kz",
    ],
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
app.include_router(request_router,        prefix="/api/v1")
app.include_router(file_router,           prefix="/api/v1")


# -------------------------
# Health Check
# -------------------------
@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": "SkillLink API"}

@app.get("/api/v1/admin/profiling", tags=["Admin"])
async def profiling_report():
    return get_latency_report()