from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.db.session import engine
from sqlmodel import SQLModel

from backend.app.api.v1.AccreditationRouter import router as accreditation_router
from backend.app.api.v1.UserRouter import router as user_router
from backend.app.api.v1.SpecialistRouter import router as specialist_router
from backend.app.api.v1.OrderRouter import router as order_router
from backend.app.api.v1.RateRouter import router as rate_router
from backend.app.api.v1.CommentRouter import router as comment_router
from backend.app.api.v1.AddressRouter import router as address_router
from backend.app.api.v1.AuthRouter import router as auth_router
from backend.app.api.v1.CatalogRouter import router as catalog_router
from backend.app.api.v1.MessageRouter import router as message_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="SkillLink API",
    description="Platform connecting clients with specialists",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router,           prefix="/api/v1")
app.include_router(user_router,           prefix="/api/v1")
app.include_router(specialist_router,     prefix="/api/v1")
app.include_router(order_router,          prefix="/api/v1")
app.include_router(catalog_router,        prefix="/api/v1")
app.include_router(rate_router,           prefix="/api/v1")
app.include_router(comment_router,        prefix="/api/v1")
app.include_router(address_router,        prefix="/api/v1")
app.include_router(accreditation_router,  prefix="/api/v1")
app.include_router(message_router,        prefix="/api/v1")

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": "SkillLink API"}