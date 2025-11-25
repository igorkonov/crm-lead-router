from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.contact import ContactResponse
from app.schemas.lead import LeadResponse, LeadUpdate
from app.services.lead_service import (
    get_lead,
    get_lead_contacts,
    update_existing_lead,
)

router = APIRouter()


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead_by_id(
    lead_id: int, db: AsyncSession = Depends(get_db)
):
    """Получить лида по ID."""
    return await get_lead(db, lead_id)


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int, lead: LeadUpdate, db: AsyncSession = Depends(get_db)
):
    """Обновить данные лида."""
    return await update_existing_lead(db, lead_id, lead)


@router.get("/leads/{lead_id}/contacts", response_model=list[ContactResponse])
async def list_lead_contacts(
    lead_id: int, db: AsyncSession = Depends(get_db)
):
    """Получить все обращения лида."""
    return await get_lead_contacts(db, lead_id)
