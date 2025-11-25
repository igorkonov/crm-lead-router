from collections import Counter

import pytest

from app.models.operator import Operator
from app.models.source import Source, SourceOperatorWeight
from app.repositories.lead_repo import create_lead
from app.schemas.lead import LeadCreate
from app.services.distribution_service import (
    distribute_contact_to_operator,
    weighted_random_choice,
)


@pytest.mark.asyncio
async def test_weighted_random_choice():
    """Проверяет базовую логику взвешенного выбора."""
    op1 = Operator(
        id=1, name="Op1", is_active=True, max_load=100, current_load=0
    )
    op2 = Operator(
        id=2, name="Op2", is_active=True, max_load=100, current_load=0
    )

    operators_with_weights = [(op1, 10), (op2, 30)]

    # Делаем 1000 выборов
    results = [
        weighted_random_choice(operators_with_weights) for _ in range(1000)
    ]
    counter = Counter(op.id for op in results)

    # Проверяем что пропорция близка к 1:3
    ratio = counter[1] / counter[2]
    assert 0.25 < ratio < 0.40  # ~0.33 с погрешностью


@pytest.mark.asyncio
async def test_weighted_distribution_proportions(db_session):
    """
    Проверяет что распределение близко к заданным весам.

    При весах 10:30 ожидаем распределение ~25%:75%
    """
    # Setup - создаем операторов
    op1 = Operator(
        name="Анна", is_active=True, max_load=100, current_load=0
    )
    op2 = Operator(
        name="Борис", is_active=True, max_load=100, current_load=0
    )
    db_session.add_all([op1, op2])
    await db_session.commit()

    # Создаем источник
    source = Source(name="Test Bot", description="Test")
    db_session.add(source)
    await db_session.commit()

    # Устанавливаем веса
    weight1 = SourceOperatorWeight(
        source_id=source.id, operator_id=op1.id, weight=10
    )
    weight2 = SourceOperatorWeight(
        source_id=source.id, operator_id=op2.id, weight=30
    )
    db_session.add_all([weight1, weight2])
    await db_session.commit()

    # Act - создаем 80 обращений (чтобы не превысить лимиты)
    assignments = []
    for i in range(80):
        lead = await create_lead(
            db_session, LeadCreate(phone=f"+7999123456{i:03d}")
        )

        operator_id = await distribute_contact_to_operator(
            db_session, lead.id, source.id
        )
        assignments.append(operator_id)

        # Увеличиваем нагрузку оператора
        if operator_id:
            if operator_id == op1.id:
                op1.current_load += 1
            elif operator_id == op2.id:
                op2.current_load += 1
            await db_session.commit()

    # Assert - проверяем пропорции
    counter = Counter(assignments)
    ratio = counter[op1.id] / counter[op2.id]

    # Ожидаем соотношение ~0.33 (10:30) с погрешностью
    # При 80 обращениях: ~20 к первому, ~60 ко второму
    assert 0.25 < ratio < 0.40


@pytest.mark.asyncio
async def test_respects_operator_limits(db_session):
    """Проверяет что не назначаем оператору больше лимита."""
    # Setup
    operator = Operator(
        name="Тест", is_active=True, max_load=5, current_load=0
    )
    db_session.add(operator)
    await db_session.commit()

    source = Source(name="Test Bot")
    db_session.add(source)
    await db_session.commit()

    weight = SourceOperatorWeight(
        source_id=source.id, operator_id=operator.id, weight=10
    )
    db_session.add(weight)
    await db_session.commit()

    # Act - создаем 10 обращений, но лимит 5
    results = []
    for i in range(10):
        lead = await create_lead(
            db_session, LeadCreate(phone=f"+7999123456{i}")
        )

        result = await distribute_contact_to_operator(
            db_session, lead.id, source.id
        )
        results.append(result)

        # Увеличиваем нагрузку вручную для теста
        if result == operator.id:
            operator.current_load += 1
            await db_session.commit()

    # Assert
    assigned = [r for r in results if r == operator.id]
    not_assigned = [r for r in results if r is None]

    assert len(assigned) == 5  # Только 5 назначений
    assert len(not_assigned) == 5  # Остальные без оператора


@pytest.mark.asyncio
async def test_no_operators_available(db_session):
    """Проверяет случай когда нет доступных операторов."""
    source = Source(name="Test Bot")
    db_session.add(source)
    await db_session.commit()

    lead = await create_lead(db_session, LeadCreate(phone="+79991234567"))

    result = await distribute_contact_to_operator(
        db_session, lead.id, source.id
    )

    assert result is None
