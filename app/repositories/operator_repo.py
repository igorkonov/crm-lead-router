from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operator import Operator
from app.models.source import SourceOperatorWeight
from app.schemas.operator import OperatorCreate, OperatorUpdate


async def get_operator_by_id(
    db: AsyncSession, operator_id: int
) -> Operator | None:
    """Получает оператора по ID."""
    result = await db.execute(
        select(Operator).where(Operator.id == operator_id)
    )
    return result.scalar_one_or_none()


async def get_all_operators(db: AsyncSession) -> list[Operator]:
    """Получает всех операторов."""
    result = await db.execute(select(Operator))
    return list(result.scalars().all())


async def get_active_operators(db: AsyncSession) -> list[Operator]:
    """Получает только активных операторов."""
    result = await db.execute(
        select(Operator).where(Operator.is_active)
    )
    return list(result.scalars().all())


async def get_operators_for_source(
    db: AsyncSession, source_id: int
) -> list[tuple[Operator, int]]:
    """
    Получает операторов для источника с их весами.

    Returns:
        Список кортежей (Operator, weight)
    """
    result = await db.execute(
        select(Operator, SourceOperatorWeight.weight)
        .join(SourceOperatorWeight)
        .where(
            SourceOperatorWeight.source_id == source_id,
            Operator.is_active,
        )
    )
    return list(result.all())


async def create_operator(
    db: AsyncSession, operator_data: OperatorCreate
) -> Operator:
    """Создает нового оператора."""
    operator = Operator(**operator_data.model_dump())
    db.add(operator)
    await db.commit()
    await db.refresh(operator)
    return operator


async def update_operator(
    db: AsyncSession, operator_id: int, operator_data: OperatorUpdate
) -> Operator | None:
    """Обновляет данные оператора."""
    operator = await get_operator_by_id(db, operator_id)
    if not operator:
        return None

    update_data = operator_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(operator, field, value)

    await db.commit()
    await db.refresh(operator)
    return operator


async def delete_operator(
    db: AsyncSession, operator_id: int
) -> bool:
    """Удаляет оператора."""
    operator = await get_operator_by_id(db, operator_id)
    if not operator:
        return False

    await db.delete(operator)
    await db.commit()
    return True


async def increment_operator_load(
    db: AsyncSession, operator_id: int
) -> None:
    """Увеличивает нагрузку оператора атомарно."""
    await db.execute(
        update(Operator)
        .where(Operator.id == operator_id)
        .values(current_load=Operator.current_load + 1)
    )
    await db.commit()


async def decrement_operator_load(
    db: AsyncSession, operator_id: int
) -> None:
    """Уменьшает нагрузку оператора атомарно."""
    await db.execute(
        update(Operator)
        .where(Operator.id == operator_id)
        .values(current_load=Operator.current_load - 1)
    )
    await db.commit()
