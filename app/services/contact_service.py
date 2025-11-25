from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.contact_repo import create_contact
from app.repositories.lead_repo import find_or_create_lead
from app.repositories.operator_repo import increment_operator_load
from app.repositories.source_repo import get_source_by_id
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.distribution_service import (
    distribute_contact_to_operator,
)


async def process_new_contact(
    db: AsyncSession, contact_data: ContactCreate
) -> ContactResponse:
    """
    Обрабатывает новое обращение клиента.

    Алгоритм:
    1. Проверить что источник существует
    2. Найти или создать лида
    3. Выбрать оператора для назначения
    4. Создать обращение
    5. Увеличить нагрузку оператора
    """
    # Guard clause: проверяем источник
    source = await get_source_by_id(db, contact_data.source_id)
    if not source:
        raise HTTPException(
            status_code=404, detail="Source not found"
        )

    # Guard clause: проверяем идентификатор лида
    if not contact_data.lead_phone and not contact_data.lead_email:
        raise HTTPException(
            status_code=400,
            detail="Either lead_phone or lead_email must be provided",
        )

    # Находим или создаем лида
    lead = await find_or_create_lead(
        db,
        phone=contact_data.lead_phone,
        email=contact_data.lead_email,
        name=contact_data.lead_name,
    )

    # Выбираем оператора
    operator_id = await distribute_contact_to_operator(
        db, lead.id, source.id
    )

    # Создаем обращение
    contact = await create_contact(
        db,
        lead_id=lead.id,
        source_id=source.id,
        operator_id=operator_id,
        message=contact_data.message,
    )

    # Увеличиваем нагрузку оператора если он назначен
    if operator_id:
        await increment_operator_load(db, operator_id)

    return ContactResponse.model_validate(contact)
