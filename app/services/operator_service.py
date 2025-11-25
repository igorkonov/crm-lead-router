from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.operator_repo import (
    create_operator,
    delete_operator,
    get_all_operators,
    get_operator_by_id,
    update_operator,
)
from app.schemas.operator import (
    OperatorCreate,
    OperatorResponse,
    OperatorUpdate,
)


async def get_operators_list(
    db: AsyncSession,
) -> list[OperatorResponse]:
    """Получает список всех операторов."""
    operators = await get_all_operators(db)
    return [OperatorResponse.model_validate(op) for op in operators]


async def get_operator(
    db: AsyncSession, operator_id: int
) -> OperatorResponse:
    """
    Получает оператора по ID.
    """
    operator = await get_operator_by_id(db, operator_id)
    if not operator:
        raise HTTPException(
            status_code=404, detail="Operator not found"
        )
    return OperatorResponse.model_validate(operator)


async def create_new_operator(
    db: AsyncSession, operator_data: OperatorCreate
) -> OperatorResponse:
    """Создает нового оператора."""
    operator = await create_operator(db, operator_data)
    return OperatorResponse.model_validate(operator)


async def update_existing_operator(
    db: AsyncSession, operator_id: int, operator_data: OperatorUpdate
) -> OperatorResponse:
    """
    Обновляет данные оператора.
    """
    operator = await update_operator(db, operator_id, operator_data)
    if not operator:
        raise HTTPException(
            status_code=404, detail="Operator not found"
        )
    return OperatorResponse.model_validate(operator)


async def delete_existing_operator(
    db: AsyncSession, operator_id: int
) -> None:
    """
    Удаляет оператора.
    """
    deleted = await delete_operator(db, operator_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Operator not found"
        )
