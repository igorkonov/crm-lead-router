from datetime import datetime

from pydantic import BaseModel, Field


class SourceBase(BaseModel):
    """Базовая схема источника."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Название источника"
    )
    description: str | None = Field(
        None, max_length=500, description="Описание"
    )


class SourceCreate(SourceBase):
    """Схема для создания источника."""

    pass


class SourceUpdate(BaseModel):
    """Схема для обновления источника."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class SourceResponse(SourceBase):
    """Схема ответа с данными источника."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceOperatorWeightCreate(BaseModel):
    """Схема для установки веса оператора для источника."""

    operator_id: int = Field(..., gt=0, description="ID оператора")
    weight: int = Field(default=10, gt=0, le=100, description="Вес оператора")


class SourceOperatorWeightResponse(BaseModel):
    """Схема ответа с весом оператора."""

    source_id: int
    operator_id: int
    weight: int

    model_config = {"from_attributes": True}


class SourceWithOperators(SourceResponse):
    """Источник с операторами и их весами."""

    operators: list[SourceOperatorWeightResponse] = Field(default_factory=list)
