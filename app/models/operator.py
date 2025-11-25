from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.source import SourceOperatorWeight


class Operator(Base, TimestampMixin):
    """
    Оператор поддержки.

    Attributes:
        id: Уникальный идентификатор
        name: Имя оператора
        is_active: Активен ли оператор (может принимать обращения)
        max_load: Максимальное количество одновременных обращений
        current_load: Текущее количество активных обращений
        source_weights: Веса для разных источников
        contacts: Обращения назначенные оператору
    """

    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    max_load: Mapped[int] = mapped_column(Integer, nullable=False)
    current_load: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    source_weights: Mapped[list[SourceOperatorWeight]] = relationship(
        "SourceOperatorWeight",
        back_populates="operator",
        cascade="all, delete-orphan",
    )
    contacts: Mapped[list[Contact]] = relationship(
        "Contact",
        back_populates="operator",
    )

    def __repr__(self) -> str:
        return (
            f"<Operator(id={self.id}, name='{self.name}', "
            f"load={self.current_load}/{self.max_load})>"
        )
