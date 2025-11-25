from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.operator import (
    OperatorCreate,
    OperatorResponse,
    OperatorUpdate,
)
from app.services.operator_service import (
    create_new_operator,
    delete_existing_operator,
    get_operator,
    get_operators_list,
    update_existing_operator,
)

router = APIRouter()


@router.get("/operators", response_model=list[OperatorResponse])
async def list_operators(db: AsyncSession = Depends(get_db)):
    """Получить список всех операторов."""
    return await get_operators_list(db)


@router.post("/operators", response_model=OperatorResponse, status_code=201)
async def create_operator(
    operator: OperatorCreate, db: AsyncSession = Depends(get_db)
):
    """Создать нового оператора."""
    return await create_new_operator(db, operator)


@router.get("/operators/{operator_id}", response_model=OperatorResponse)
async def get_operator_by_id(
    operator_id: int, db: AsyncSession = Depends(get_db)
):
    """Получить оператора по ID."""
    return await get_operator(db, operator_id)


@router.patch("/operators/{operator_id}", response_model=OperatorResponse)
async def update_operator(
    operator_id: int,
    operator: OperatorUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновить данные оператора."""
    return await update_existing_operator(db, operator_id, operator)


@router.delete("/operators/{operator_id}", status_code=204)
async def delete_operator(
    operator_id: int, db: AsyncSession = Depends(get_db)
):
    """Удалить оператора."""
    await delete_existing_operator(db, operator_id)
