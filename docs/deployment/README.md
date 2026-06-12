# Deployment Documentation

Этот раздел содержит документацию по развёртыванию Creative Test Agent на сервере и локально.

## Состав

| Документ | Описание |
|----------|----------|
| `local_server_setup.md` | Запуск локально и на сервере |
| `docker_setup.md` | Docker сборка и запуск |
| `env_reference.md` | Справочник всех env переменных |
| `server_checklist_ru.md` | Чеклист проверки сервера перед демо |

## Быстрый старт

```bash
# Локально
uvicorn src.main:app --reload --port 8000

# На сервере
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Через Docker
docker compose up --build
```

## Ограничения MVP

- SQLite не рассчитан на высокие конкурентные нагрузки.
- Нет разграничения прав пользователей (auth disabled by default).
- Нет production-аутентификации.
- Restic-режим использует детерминированные правила.
- Рекомендуется для pilot-нагрузки, не для production-scale.
