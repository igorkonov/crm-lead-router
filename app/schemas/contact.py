from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    """Базовая схема обращения."""

    message: str | None = Field(None, description="Текст сообщения")


class ContactCreate(ContactBase):
    """
    Схема для создания обращения.

    Клиент идентифицируется по телефону или email.
    """

    source_id: int = Field(..., gt=0, description="ID источника")
    lead_phone: str | None = Field(
        None, max_length=20, description="Телефон клиента"
    )
    lead_email: EmailStr | None = Field(
        None, description="Email клиента"
    )
    lead_name: str | None = Field(
        None, max_length=255, description="Имя клиента"
    )


class ContactResponse(ContactBase):
    """Схема ответа с данными обращения."""

    id: int
    lead_id: int
    source_id: int
    operator_id: int | None = Field(
        None, description="ID назначенного оператора"
    )
    is_resolved: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContactWithDetails(ContactResponse):
    """Обращение с полной информацией о лиде и операторе."""

    lead_phone: str | None = None
    lead_email: str | None = None
    lead_name: str | None = None
    operator_name: str | None = None
    source_name: str | None = None
