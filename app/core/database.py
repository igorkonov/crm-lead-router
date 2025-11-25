from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)


async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    Dependency для получения асинхронной сессии БД.
    """
    async with async_session_maker() as session:
        yield session


async def init_database() -> None:
    """
    Инициализация базы данных при старте приложения.
    """
    pass


async def close_database() -> None:
    """Закрытие соединений с БД при остановке приложения."""
    await engine.dispose()
