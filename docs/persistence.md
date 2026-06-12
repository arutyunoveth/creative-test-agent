# Persistence Layer

This document describes how Creative Test Agent stores and manages its data.

## Что сохраняется

Все сущности, создаваемые через API или UI, сохраняются в реляционную базу данных:

| Entity | Table | Description |
|---|---|---|
| Creative Assets | `creative_asset` | Загруженные креативы (текст, файлы) |
| Brand Profiles | `brand_profile` | Профили брендов с tone-of-voice, ограничениями |
| Audience Profiles | `audience_profile` | Профили целевых аудиторий |
| Test Rubrics | `test_rubric` | Критерии оценки креативов |
| Test Runs | `test_run` | Результаты тестовых прогонов |
| Reports | `report` | Сгенерированные отчёты (версионированные) |
| Audit Events | `audit_event` | Аудит-лог всех операций |

## Где хранится

По умолчанию используется SQLite:

```
CTA_DATABASE_URL=sqlite:///./creative_test_agent.db
```

Переменная окружения `CTA_DATABASE_URL` задаёт путь к файлу БД. Файл создаётся автоматически при первом запуске сервера.

## Как инициализируется БД

### Через app startup

При запуске `uvicorn src.main:app --reload` вызывается `init_db()`, который:

1. Импортирует все модели SQLAlchemy (чтобы они зарегистрировались в `Base.metadata`);
2. Вызывает `Base.metadata.create_all()` — создаёт таблицы, если их нет.

### Через Alembic (для миграций)

В проекте настроен Alembic (см. `alembic.ini` и `migrations/`).

Создать миграцию после изменения моделей:

```bash
PYTHONPATH=. alembic revision --autogenerate -m "description"
```

Применить миграции:

```bash
PYTHONPATH=. alembic upgrade head
```

Первая миграция создаёт все 7 таблиц:

```
migrations/versions/a5e3aa24e284_initial_persistence_schema.py
```

Текущая архитектура использует `create_all()` как основной способ инициализации,
а Alembic добавлен как future path для управления изменениями схемы.

## Как проверить БД

```bash
curl http://localhost:8000/health/db
```

Response:

```json
{
  "status": "ok",
  "database": "connected",
  "database_url": "sqlite:///./creative_test_agent.db"
}
```

Если в URL есть пароль, он маскируется (заменяется на `****`).

## Как сбросить demo data

```bash
python scripts/reset_demo_data.py
```

Скрипт удаляет все сущности, у которых `metadata.demo == True`.
Пользовательские данные (без demo-метки) не удаляются.

## Как экспортировать pilot data

```bash
python scripts/export_pilot_data.py
```

Export сохраняется в:

```
data/exports/pilot_export_YYYYMMDD_HHMMSS.json
```

Структура JSON:

```json
{
  "exported_at": "2026-06-11T18:00:00",
  "app": "Creative Test Agent",
  "brand_profiles": [],
  "audience_profiles": [],
  "creative_assets": [...],
  "test_rubrics": [],
  "test_runs": [],
  "reports": [],
  "audit_events": []
}
```

## Как засеять demo данные

```bash
python scripts/seed_demo_data.py
```

Сценарий: "NovaBank Freelancer Card" — три варианта креатива для фрилансеров.

Идемпотентен: проверяет существование entities по имени/title перед созданием.

## Ограничения

- **SQLite** подходит для локального пилота, но не предназначен для production multi-user сценариев.
- **PostgreSQL** можно добавить позже через CTA_DATABASE_URL (SQLAlchemy поддерживает).
- **Production auth** не реализован — проект local-first.
- **Uploaded files** хранятся отдельно в `data/storage/` (не в JSON export).
- **Alembic** настроен, но `create_all()` является основным методом инициализации.
  Alembic следует использовать для управления миграциями при изменении схемы.

## Future Path

- [ ] Миграция на Alembic как основной способ управления схемой
- [ ] Production-ready connection pooling для PostgreSQL
- [ ] Шифрование чувствительных полей
- [ ] Backups и точка восстановления
- [ ] Миграция uploaded files в объектное хранилище (S3-compatible)
