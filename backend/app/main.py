"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import companions, contacts, calls, webhooks, oauth
from app.config import settings
from app.lib.log import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Hookline starting (env=%s)", settings.app_env)
    yield
    logger.info("Hookline shutting down")


app = FastAPI(
    title="Hookline",
    description="Programmable voice companion platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow dashboard + CF worker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_dev else ["https://hookline.autonolabs.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(companions.router)
app.include_router(contacts.router)
app.include_router(calls.router)
app.include_router(webhooks.router)
app.include_router(oauth.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/")
async def root():
    return {"app": "Hookline", "docs": "/docs", "version": "0.1.0"}
