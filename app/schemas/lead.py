from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LeadBase(BaseModel):
    """Базовая схема лида."""

    phone: str | None = Field(None, max_length=20, description="Телефон")
    email: EmailStr | None = Field(None, description="Email")
    name: str | None = Field(None, max_length=255, description="Имя")


class LeadCreate(LeadBase):
    """Схема для создания лида."""

    pass


class LeadUpdate(BaseModel):
    """Схема для обновления лида."""

    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    name: str | None = Field(None, max_length=255)


class LeadResponse(LeadBase):
    """Схема ответа с данными лида."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
