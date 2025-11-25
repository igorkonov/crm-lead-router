from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.lead import Lead
    from app.models.operator import Operator
    from app.models.source import Source


class Contact(Base, TimestampMixin):
    """
    Обращение клиента.

    Конкретное сообщение от клиента через определенный источник.
    Может быть назначено оператору или остаться без назначения если все заняты.

    Attributes:
        id: Уникальный идентификатор
        lead_id: ID клиента
        source_id: ID источника откуда пришло обращение
        operator_id: ID назначенного оператора (может быть None)
        message: Текст сообщения
        is_resolved: Обработано ли обращение
        lead: Клиент который обратился
        source: Источник обращения
        operator: Назначенный оператор
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    lead_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operator_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("operators.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(default=False, nullable=False)

    lead: Mapped[Lead] = relationship("Lead", back_populates="contacts")
    source: Mapped[Source] = relationship("Source", back_populates="contacts")
    operator: Mapped[Operator | None] = relationship(
        "Operator", back_populates="contacts"
    )

    def __repr__(self) -> str:
        return (
            f"<Contact(id={self.id}, lead_id={self.lead_id}, "
            f"operator_id={self.operator_id})>"
        )
