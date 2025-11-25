from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.operator import Operator


class Source(Base, TimestampMixin):
    """
    Источник обращений.

    Attributes:
        id: Уникальный идентификатор
        name: Название источника (например "Telegram Bot", "WhatsApp")
        description: Описание источника
        operator_weights: Веса операторов для этого источника
        contacts: Обращения из этого источника
    """

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    operator_weights: Mapped[list[SourceOperatorWeight]] = relationship(
        "SourceOperatorWeight",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    contacts: Mapped[list[Contact]] = relationship(
        "Contact",
        back_populates="source",
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, name='{self.name}')>"


class SourceOperatorWeight(Base):
    """
    Вес оператора для конкретного источника.

    Определяет приоритет назначения оператора для обращений из источника.
    Чем больше вес, тем выше вероятность назначения.

    Attributes:
        source_id: ID источника
        operator_id: ID оператора
        weight: Вес (приоритет) оператора для этого источника
    """

    __tablename__ = "source_operator_weights"

    source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    )
    operator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("operators.id", ondelete="CASCADE"),
        primary_key=True,
    )
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    source: Mapped[Source] = relationship(
        "Source",
        back_populates="operator_weights",
    )
    operator: Mapped[Operator] = relationship(
        "Operator",
        back_populates="source_weights",
    )

    def __repr__(self) -> str:
        return (
            f"<SourceOperatorWeight(source_id={self.source_id}, "
            f"operator_id={self.operator_id}, weight={self.weight})>"
        )
