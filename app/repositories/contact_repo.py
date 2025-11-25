from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.contact import Contact


async def get_contact_by_id(
    db: AsyncSession, contact_id: int
) -> Contact | None:
    """Получает обращение по ID."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    return result.scalar_one_or_none()


async def get_contact_with_details(
    db: AsyncSession, contact_id: int
) -> Contact | None:
    """Получает обращение со всеми связанными данными."""
    result = await db.execute(
        select(Contact)
        .options(
            joinedload(Contact.lead),
            joinedload(Contact.source),
            joinedload(Contact.operator),
        )
        .where(Contact.id == contact_id)
    )
    return result.unique().scalar_one_or_none()


async def get_contacts_by_lead(
    db: AsyncSession, lead_id: int
) -> list[Contact]:
    """Получает все обращения лида."""
    result = await db.execute(
        select(Contact).where(Contact.lead_id == lead_id)
    )
    return list(result.scalars().all())


async def get_contacts_by_operator(
    db: AsyncSession, operator_id: int, resolved: bool | None = None
) -> list[Contact]:
    """
    Получает обращения оператора.

    Args:
        db: Сессия БД
        operator_id: ID оператора
        resolved: Фильтр по статусу (None = все)

    Returns:
        Список обращений
    """
    query = select(Contact).where(Contact.operator_id == operator_id)

    if resolved is not None:
        query = query.where(Contact.is_resolved == resolved)

    result = await db.execute(query)
    return list(result.scalars().all())


async def create_contact(
    db: AsyncSession,
    lead_id: int,
    source_id: int,
    operator_id: int | None,
    message: str | None = None,
) -> Contact:
    """Создает новое обращение."""
    contact = Contact(
        lead_id=lead_id,
        source_id=source_id,
        operator_id=operator_id,
        message=message,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def resolve_contact(
    db: AsyncSession, contact_id: int
) -> Contact | None:
    """Помечает обращение как обработанное."""
    contact = await get_contact_by_id(db, contact_id)
    if not contact:
        return None

    contact.is_resolved = True
    await db.commit()
    await db.refresh(contact)
    return contact
