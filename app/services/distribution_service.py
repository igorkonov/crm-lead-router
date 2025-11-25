import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operator import Operator
from app.repositories.operator_repo import get_operators_for_source


async def select_operator_for_source(
    db: AsyncSession, source_id: int, lead_id: int
) -> Operator | None:
    """
    Выбирает оператора для обращения из источника.

    Алгоритм:
    1. Получить операторов для источника с весами
    2. Отфильтровать перегруженных и неактивных
    3. Выбрать случайно с вероятностью пропорциональной весу
    4. Вернуть ID оператора или None если никто не доступен
    """
    # 1. Получаем операторов с весами
    operators_with_weights = await get_operators_for_source(db, source_id)
    if not operators_with_weights:
        return None

    # 2. Фильтруем доступных (активных и не перегруженных)
    available = [
        (operator, weight)
        for operator, weight in operators_with_weights
        if operator.is_active and operator.current_load < operator.max_load
    ]

    if not available:
        return None

    # 3. Взвешенный случайный выбор
    return weighted_random_choice(available)


def weighted_random_choice(
    operators_with_weights: list[tuple[Operator, int]]
) -> Operator:
    """
    Выбирает оператора взвешенным случайным методом.
    Вероятность выбора пропорциональна весу оператора.
    """
    if not operators_with_weights:
        raise ValueError("Список операторов пуст")

    operators, weights = zip(*operators_with_weights, strict=False)
    total_weight = sum(weights)

    if total_weight == 0:
        # Если все веса 0, выбираем случайно
        return random.choice(operators)

    # Генерируем случайное число от 0 до total_weight
    random_value = random.uniform(0, total_weight)

    # Находим оператора соответствующего этому значению
    cumulative = 0
    for operator, weight in operators_with_weights:
        cumulative += weight
        if random_value <= cumulative:
            return operator

    # Fallback на последнего (на случай ошибок округления)
    return operators[-1]


async def distribute_contact_to_operator(
    db: AsyncSession, lead_id: int, source_id: int
) -> int | None:
    """
    Распределяет обращение на оператора.
    Возвращает ID выбранного оператора или None.
    """
    operator = await select_operator_for_source(db, source_id, lead_id)
    return operator.id if operator else None
