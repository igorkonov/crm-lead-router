from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.source_repo import (
    create_source,
    delete_source,
    get_all_sources,
    get_operator_weights,
    get_source_by_id,
    set_operator_weight,
    update_source,
)
from app.schemas.source import (
    SourceCreate,
    SourceOperatorWeightCreate,
    SourceOperatorWeightResponse,
    SourceResponse,
    SourceUpdate,
)


async def get_sources_list(db: AsyncSession) -> list[SourceResponse]:
    """Получает список всех источников."""
    sources = await get_all_sources(db)
    return [SourceResponse.model_validate(s) for s in sources]


async def get_source(
    db: AsyncSession, source_id: int
) -> SourceResponse:
    """
    Получает источник по ID.
    """
    source = await get_source_by_id(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceResponse.model_validate(source)


async def create_new_source(
    db: AsyncSession, source_data: SourceCreate
) -> SourceResponse:
    """Создает новый источник."""
    source = await create_source(db, source_data)
    return SourceResponse.model_validate(source)


async def update_existing_source(
    db: AsyncSession, source_id: int, source_data: SourceUpdate
) -> SourceResponse:
    """
    Обновляет данные источника.
    """
    source = await update_source(db, source_id, source_data)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceResponse.model_validate(source)


async def delete_existing_source(
    db: AsyncSession, source_id: int
) -> None:
    """
    Удаляет источник.
    """
    deleted = await delete_source(db, source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")


async def set_source_operator_weight(
    db: AsyncSession,
    source_id: int,
    weight_data: SourceOperatorWeightCreate,
) -> SourceOperatorWeightResponse:
    """
    Устанавливает вес оператора для источника.
    """
    # Проверяем что источник существует
    source = await get_source_by_id(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    weight_record = await set_operator_weight(
        db, source_id, weight_data.operator_id, weight_data.weight
    )
    return SourceOperatorWeightResponse.model_validate(weight_record)


async def get_source_operator_weights(
    db: AsyncSession, source_id: int
) -> list[SourceOperatorWeightResponse]:
    """
    Получает веса операторов для источника.
    """
    source = await get_source_by_id(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    weights = await get_operator_weights(db, source_id)
    return [
        SourceOperatorWeightResponse.model_validate(w) for w in weights
    ]
