from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.db.session import engine
import backend.app.db.models
from sqlmodel import SQLModel


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



@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": "SkillLink API"}