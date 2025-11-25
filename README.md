# CRM Lead Router

Сервис для автоматического распределения обращений клиентов между операторами.

## Как работает

Когда клиент пишет в бот, система:
1. Находит этого клиента или создает нового (по телефону/email)
2. Смотрит из какого бота пришло сообщение
3. Выбирает оператора который работает с этим ботом
4. Учитывает сколько у оператора сейчас активных клиентов
5. Распределяет по весам (если у оператора вес 30, а у другого 10, то первый получит примерно в 3 раза больше обращений)

## Быстрый старт

### Вариант 1: Docker

```bash
# Запуск
docker-compose up --build

# В фоне
docker-compose up -d

# Остановка
docker-compose down
```

### Вариант 2: Локально

```bash
# Установка зависимостей
uv sync

# Миграции
uv run alembic upgrade head

# Запуск
uv run uvicorn app.main:app --reload
```

Открываем http://localhost:8000/docs

## Примеры использования

### Создать оператора

```bash
curl -X POST http://localhost:8000/api/v1/operators \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Анна",
    "is_active": true,
    "max_load": 50
  }'
```

Ответ:

```json
{
  "name": "Анна",
  "is_active": true,
  "max_load": 50,
  "id": 1,
  "current_load": 0,
  "created_at": "2025-11-26T00:00:00",
  "updated_at": "2025-11-26T00:00:00"
}
```

### Создать источник (бот)

```bash
curl -X POST http://localhost:8000/api/v1/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Telegram Bot",
    "description": "Основной телеграм бот"
  }'
```

### Установить вес оператора для источника

```bash
curl -X POST http://localhost:8000/api/v1/sources/1/operators \
  -H "Content-Type: application/json" \
  -d '{
    "operator_id": 1,
    "weight": 30
  }'
```

Ответ:

```json
{
  "source_id": 1,
  "operator_id": 1,
  "weight": 30
}
```

### Зарегистрировать обращение

```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "lead_phone": "+79991234567",
    "source_id": 1,
    "message": "Здравствуйте!"
  }'
```

Ответ:

```json
{
  "message": "Здравствуйте!",
  "id": 1,
  "lead_id": 1,
  "source_id": 1,
  "operator_id": 1,
  "is_resolved": false,
  "created_at": "2025-11-26T00:00:00",
  "updated_at": "2025-11-26T00:00:00"
}
```

> **Примечание:** Если все операторы перегружены, `operator_id` будет `null`

## Модели данных

### Operator - оператор поддержки

- Может быть активен/неактивен
- Имеет лимит одновременных клиентов (`max_load`: 1-100)
- Для каждого бота имеет вес (приоритет)

### Lead - клиент

- Идентифицируется по телефону/email
- Может писать из разных ботов
- Система понимает что это один человек

### Source - бот/канал откуда пришло сообщение

- Telegram bot, WhatsApp, сайт и тд
- Для каждого настроены операторы с весами

### Contact - конкретное обращение

- Связано с клиентом и источником
- Имеет назначенного оператора (или `null` если все заняты)

## Алгоритм распределения

Используется **weighted random selection**:

- Вероятность назначения = вес_оператора / сумма_весов
- Если выбранный оператор перегружен - выбираем другого
- Если все перегружены - создаем обращение без оператора (`operator_id = null`)

**Пример:** для бота A у Анны вес 10, у Бориса 30 → Анна получит ~25% обращений, Борис ~75%

## Технологии

- FastAPI + async/await
- SQLAlchemy 2.0 (async)
- SQLite + aiosqlite
- Pydantic v2
- uv для зависимостей
- Alembic для миграций
- Docker + Docker Compose

## Тестирование

```bash
# Запуск тестов
uv run pytest

# С покрытием
uv run pytest --cov=app

# Конкретный тест
uv run pytest tests/test_distribution.py::test_weighted_distribution_proportions
```

### Тестирование в Docker

```bash
# Запустить тесты в контейнере
docker-compose run --rm app uv run pytest

# С покрытием
docker-compose run --rm app uv run pytest --cov=app
```

## Структура проекта

```text
crm-lead-router/
├── app/
│   ├── main.py              # FastAPI приложение
│   ├── core/                # Конфигурация и БД
│   ├── models/              # SQLAlchemy модели
│   ├── schemas/             # Pydantic схемы
│   ├── services/            # Бизнес-логика
│   ├── repositories/        # Работа с БД
│   └── api/v1/              # API endpoints
├── alembic/                 # Миграции БД
├── scripts/                 # Вспомогательные скрипты
├── tests/                   # Тесты
└── pyproject.toml           # Зависимости
```

## Разработка

```bash
# Линтинг
uv run ruff check .

# Форматирование
uv run ruff format .

# Создать миграцию
uv run alembic revision --autogenerate -m "описание"

# Применить миграции
uv run alembic upgrade head
```

## Скрипты для тестирования

В папке `scripts/` есть вспомогательные скрипты:

```bash
# Тест распределения - создает 100 обращений и показывает статистику
./scripts/test_distribution.sh
```

### Особенности

- База данных SQLite монтируется как volume для сохранения данных
- Миграции применяются автоматически при старте
- Приложение доступно на http://localhost:8000
- Swagger документация на http://localhost:8000/docs
