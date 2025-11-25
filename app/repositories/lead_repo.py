from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


async def get_lead_by_id(db: AsyncSession, lead_id: int) -> Lead | None:
    """Получает лида по ID."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    return result.scalar_one_or_none()


async def find_lead_by_identifier(
    db: AsyncSession, phone: str | None = None, email: str | None = None
) -> Lead | None:
    """
    Ищет лида по телефону или email.

    Args:
        db: Сессия БД
        phone: Телефон для поиска
        email: Email для поиска

    Returns:
        Найденный лид или None
    """
    if not phone and not email:
        return None

    conditions = []
    if phone:
        conditions.append(Lead.phone == phone)
    if email:
        conditions.append(Lead.email == email)

    result = await db.execute(select(Lead).where(or_(*conditions)))
    return result.scalar_one_or_none()


async def create_lead(db: AsyncSession, lead_data: LeadCreate) -> Lead:
    """Создает нового лида."""
    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


async def update_lead(
    db: AsyncSession, lead_id: int, lead_data: LeadUpdate
) -> Lead | None:
    """Обновляет данные лида."""
    lead = await get_lead_by_id(db, lead_id)
    if not lead:
        return None

    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    await db.commit()
    await db.refresh(lead)
    return lead


async def find_or_create_lead(
    db: AsyncSession,
    phone: str | None = None,
    email: str | None = None,
    name: str | None = None,
) -> Lead:
    """
    Находит существующего лида или создает нового.

    Args:
        db: Сессия БД
        phone: Телефон
        email: Email
        name: Имя

    Returns:
        Найденный или созданный лид
    """
    # Пытаемся найти существующего
    lead = await find_lead_by_identifier(db, phone, email)
    if lead:
        # Обновляем имя если оно передано и отличается
        if name and lead.name != name:
            lead.name = name
            await db.commit()
            await db.refresh(lead)
        return lead

    # Создаем нового
    lead_data = LeadCreate(phone=phone, email=email, name=name)
    return await create_lead(db, lead_data)
