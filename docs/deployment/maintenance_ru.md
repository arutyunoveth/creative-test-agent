# Обслуживание сервера

## Команды Makefile

```bash
# Миграции
make migrations-check     # Проверить статус миграций
make migrations-upgrade   # Применить миграции до последней версии

# Bootstrap admin
make bootstrap-admin      # Создать администратора

# Server readiness
make check-server         # Полная проверка сервера

# Docker server
make server-build         # Собрать Docker образ
make server-up            # Запустить контейнер
make server-down          # Остановить контейнер
make server-logs          # Просмотр логов
make server-shell         # Войти в shell контейнера
make server-check         # Проверить readiness через Docker
make server-bootstrap-admin  # Создать admin через Docker
make server-backup        # Создать backup
make server-restore       # Восстановить backup
```

## Maintenance UI

Откройте в браузере:

```
http://localhost:8000/ui/admin/maintenance
```

Страница показывает:

- Статус окружения (env, провайдеры)
- Статус базы данных (подключена, таблицы)
- Статус хранилища (доступно для записи, размер, файлы)
- Статус миграций (текущая головная ревизия, ревизия БД)
- Closed-loop статус
- Статус резервного копирования

Если `CTA_ENABLE_AUTH=true`, страница требует роль admin или manager.

## API Maintenance Endpoints

Доступны программные эндпоинты (с auth admin role, если включена):

| Endpoint | Описание |
|----------|----------|
| `GET /admin/maintenance/status` | Общий статус системы |
| `GET /admin/maintenance/storage` | Статус хранилища (размер, файлы) |
| `GET /admin/maintenance/database` | Статус БД (таблицы, миграции) |

## Миграции

```bash
# Проверить статус
python scripts/check_migrations.py

# Применить миграции
python scripts/run_migrations.py
```

`check_migrations.py` выводит:
- Доступна ли БД
- Текущая head-ревизия Alembic
- Текущая ревизия БД
- Совпадают ли они

## Серверные логгеры

Настройка логирования:

```env
CTA_LOG_LEVEL=INFO
CTA_LOG_FORMAT=plain
CTA_LOG_FILE=
```

- `CTA_LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `CTA_LOG_FORMAT`: `plain` (по умолчанию) — простой формат
- `CTA_LOG_FILE`: путь к файлу лога (пусто = вывод в консоль)

## Операционные аудит-события

Система логирует ключевые операции:

| Событие | Когда |
|---------|-------|
| `maintenance_status_requested` | Запрос статуса maintenance |
| `backup_created` | Создание backup |
| `backup_restore_started` | Начало восстановления |
| `backup_restore_completed` | Успешное восстановление |
| `backup_restore_failed` | Ошибка восстановления |
| `migration_check_completed` | Проверка миграций |
| `migration_upgrade_completed` | Применение миграций |

События видны в таблице `audit_event` и через `GET /audit-log`.
