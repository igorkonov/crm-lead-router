from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import contacts, leads, operators, sources
from app.core.config import settings
from app.core.database import close_database, init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

# Подключаем роутеры
app.include_router(operators.router, prefix="/api/v1", tags=["operators"])
app.include_router(sources.router, prefix="/api/v1", tags=["sources"])
app.include_router(leads.router, prefix="/api/v1", tags=["leads"])
app.include_router(contacts.router, prefix="/api/v1", tags=["contacts"])


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "message": "CRM Lead Router API",
        "docs": "/docs",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
