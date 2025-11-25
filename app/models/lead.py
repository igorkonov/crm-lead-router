from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contact import Contact


class Lead(Base, TimestampMixin):
    """
    Лид (клиент).

    Один клиент может писать из разных ботов/каналов,
    но система понимает что это один человек.

    Attributes:
        id: Уникальный идентификатор
        phone: Телефон клиента (уникальный идентификатор)
        email: Email клиента (опционально)
        name: Имя клиента (опционально)
        contacts: Все обращения этого клиента
    """

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True, index=True
    )
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    contacts: Mapped[list[Contact]] = relationship(
        "Contact",
        back_populates="lead",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        identifier = self.phone or self.email or f"id={self.id}"
        return f"<Lead({identifier})>"
