from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.emails import router as emails_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Support Service", lifespan=lifespan)
app.include_router(emails_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
