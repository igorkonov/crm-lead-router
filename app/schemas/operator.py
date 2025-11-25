from datetime import datetime

from pydantic import BaseModel, Field


class OperatorBase(BaseModel):
    """Базовая схема оператора."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Имя оператора"
    )
    is_active: bool = Field(default=True, description="Активен ли оператор")
    max_load: int = Field(gt=0, le=100, description="Максимальная нагрузка")


class OperatorCreate(OperatorBase):
    """Схема для создания оператора."""

    pass


class OperatorUpdate(BaseModel):
    """Схема для обновления оператора."""

    name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None
    max_load: int | None = Field(None, gt=0, le=100)


class OperatorResponse(OperatorBase):
    """Схема ответа с данными оператора."""

    id: int
    current_load: int = Field(description="Текущая нагрузка")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OperatorWithWeights(OperatorResponse):
    """Оператор с весами для источников."""

    weights: dict[int, int] = Field(
        default_factory=dict,
        description="Словарь {source_id: weight}",
    )
