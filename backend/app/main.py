from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import logfire
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, reports, research, webhooks
from app.api.websocket import router as ws_router
from app.config import settings
from app.database import engine

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Schema is managed by Alembic: `uv run alembic upgrade head`
    log.info("starting_up", env=settings.APP_ENV)
    yield
    log.info("shutting_down")
    await engine.dispose()


app = FastAPI(
    title="Parallax API",
    description="Multi-Agent Research Network",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url=None,
)

# Observability
if settings.LOGFIRE_TOKEN:
    logfire.configure(token=settings.LOGFIRE_TOKEN)
    logfire.instrument_fastapi(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(research.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(ws_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.APP_ENV}
