from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.contact_repo import get_contacts_by_lead
from app.repositories.lead_repo import get_lead_by_id, update_lead
from app.schemas.contact import ContactResponse
from app.schemas.lead import LeadResponse, LeadUpdate


async def get_lead(db: AsyncSession, lead_id: int) -> LeadResponse:
    """
    Получает лида по ID.
    """
    lead = await get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


async def update_existing_lead(
    db: AsyncSession, lead_id: int, lead_data: LeadUpdate
) -> LeadResponse:
    """
    Обновляет данные лида.
    """
    lead = await update_lead(db, lead_id, lead_data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


async def get_lead_contacts(
    db: AsyncSession, lead_id: int
) -> list[ContactResponse]:
    """
    Получает все обращения лида.
    """
    # Проверяем что лид существует
    lead = await get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    contacts = await get_contacts_by_lead(db, lead_id)
    return [ContactResponse.model_validate(c) for c in contacts]
