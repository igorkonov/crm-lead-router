from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source, SourceOperatorWeight
from app.schemas.source import SourceCreate, SourceUpdate


async def get_source_by_id(
    db: AsyncSession, source_id: int
) -> Source | None:
    """Получает источник по ID."""
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    return result.scalar_one_or_none()


async def get_all_sources(db: AsyncSession) -> list[Source]:
    """Получает все источники."""
    result = await db.execute(select(Source))
    return list(result.scalars().all())


async def create_source(
    db: AsyncSession, source_data: SourceCreate
) -> Source:
    """Создает новый источник."""
    source = Source(**source_data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


async def update_source(
    db: AsyncSession, source_id: int, source_data: SourceUpdate
) -> Source | None:
    """Обновляет данные источника."""
    source = await get_source_by_id(db, source_id)
    if not source:
        return None

    update_data = source_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)

    await db.commit()
    await db.refresh(source)
    return source


async def delete_source(db: AsyncSession, source_id: int) -> bool:
    """Удаляет источник."""
    source = await get_source_by_id(db, source_id)
    if not source:
        return False

    await db.delete(source)
    await db.commit()
    return True


async def set_operator_weight(
    db: AsyncSession, source_id: int, operator_id: int, weight: int
) -> SourceOperatorWeight:
    """Устанавливает вес оператора для источника."""
    # Проверяем существует ли уже запись
    result = await db.execute(
        select(SourceOperatorWeight).where(
            SourceOperatorWeight.source_id == source_id,
            SourceOperatorWeight.operator_id == operator_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.weight = weight
        await db.commit()
        await db.refresh(existing)
        return existing

    # Создаем новую запись
    weight_record = SourceOperatorWeight(
        source_id=source_id, operator_id=operator_id, weight=weight
    )
    db.add(weight_record)
    await db.commit()
    await db.refresh(weight_record)
    return weight_record


async def get_operator_weights(
    db: AsyncSession, source_id: int
) -> list[SourceOperatorWeight]:
    """Получает все веса операторов для источника."""
    result = await db.execute(
        select(SourceOperatorWeight).where(
            SourceOperatorWeight.source_id == source_id
        )
    )
    return list(result.scalars().all())
