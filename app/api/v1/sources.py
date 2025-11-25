from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.source import (
    SourceCreate,
    SourceOperatorWeightCreate,
    SourceOperatorWeightResponse,
    SourceResponse,
    SourceUpdate,
)
from app.services.source_service import (
    create_new_source,
    delete_existing_source,
    get_source,
    get_source_operator_weights,
    get_sources_list,
    set_source_operator_weight,
    update_existing_source,
)

router = APIRouter()


@router.get("/sources", response_model=list[SourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    """Получить список всех источников."""
    return await get_sources_list(db)


@router.post("/sources", response_model=SourceResponse, status_code=201)
async def create_source(
    source: SourceCreate, db: AsyncSession = Depends(get_db)
):
    """Создать новый источник."""
    return await create_new_source(db, source)


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source_by_id(
    source_id: int, db: AsyncSession = Depends(get_db)
):
    """Получить источник по ID."""
    return await get_source(db, source_id)


@router.patch("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source: SourceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновить данные источника."""
    return await update_existing_source(db, source_id, source)


@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(
    source_id: int, db: AsyncSession = Depends(get_db)
):
    """Удалить источник."""
    await delete_existing_source(db, source_id)


@router.post(
    "/sources/{source_id}/operators",
    response_model=SourceOperatorWeightResponse,
    status_code=201,
)
async def set_operator_weight(
    source_id: int,
    weight: SourceOperatorWeightCreate,
    db: AsyncSession = Depends(get_db),
):
    """Установить вес оператора для источника."""
    return await set_source_operator_weight(db, source_id, weight)


@router.get(
    "/sources/{source_id}/operators",
    response_model=list[SourceOperatorWeightResponse],
)
async def get_operator_weights(
    source_id: int, db: AsyncSession = Depends(get_db)
):
    """Получить веса операторов для источника."""
    return await get_source_operator_weights(db, source_id)
