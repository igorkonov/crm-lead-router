from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import process_new_contact

router = APIRouter()


@router.post("/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact: ContactCreate, db: AsyncSession = Depends(get_db)
):
    """
    Создать новое обращение.

    Автоматически находит или создает лида и назначает оператора.
    """
    return await process_new_contact(db, contact)
