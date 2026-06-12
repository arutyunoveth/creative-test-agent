# Руководство по развёртыванию сервера

Это руководство описывает развёртывание Creative Test Agent на сервере для пилотного использования.

## Требования

- Linux-сервер (Ubuntu 22.04+ / Debian 12+)
- Docker и Docker Compose (рекомендовано)
- Python 3.11+ (если без Docker)
- Минимум 1 GB RAM, 5 GB дискового пространства

## Варианты развёртывания

### 1. Docker (рекомендовано)

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd creative-test-agent

# 2. Создать .env.server из примера
cp .env.server.example .env.server
nano .env.server  # отредактировать настройки

# 3. Собрать и запустить
make server-build
make server-up

# 4. Создать администратора
make server-bootstrap-admin

# 5. Проверить готовность
make server-check
```

Приложение доступно по адресу `http://<server-ip>:8000/`.

### 2. Без Docker (Python напрямую)

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd creative-test-agent

# 2. Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# 3. Установить зависимости
pip install -e ".[dev]"

# 4. Создать .env из примера
cp .env.server.example .env.server
# Переименовать в .env для локального запуска
cp .env.server .env
nano .env  # отредактировать

# 5. Применить миграции
make migrations-upgrade

# 6. Создать администратора
make bootstrap-admin

# 7. Запустить
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Настройка .env.server

Все настройки с префиксом `CTA_`. Пример:

```env
CTA_ENV=server
CTA_HOST=0.0.0.0
CTA_PORT=8000
CTA_SECRET_KEY=<сгенерируйте надёжный ключ>
CTA_ENABLE_AUTH=true
CTA_DATABASE_URL=sqlite:///./data/db/creative_test_agent.db
```

**Важно:**
- `CTA_SECRET_KEY` должен быть уникальным, надёжным значением
- Для пилота рекомендуется `CTA_LLM_PROVIDER=stub` (заглушка без LLM)
- Все пути создаются автоматически при запуске

## Проверка работоспособности

```bash
# Полная проверка (локально)
make check-server

# Проверка через Docker
make server-check

# Проверка миграций
make migrations-check
```

## Обновление приложения

```bash
# 1. Создать backup перед обновлением
python scripts/backup_data.py

# 2. Скачать новую версию
git pull

# 3. Пересобрать Docker образ
make server-build

# 4. Перезапустить
make server-down
make server-up

# 5. Применить новые миграции
make migrations-upgrade  # через .venv
# или
make server-shell  # затем внутри контейнера:
# python scripts/run_migrations.py
```

## Откат

```bash
# 1. Остановить приложение
make server-down

# 2. Восстановить предыдущую версию кода
git checkout <previous-tag>

# 3. Восстановить данные из backup
python scripts/restore_data.py data/backups/cta_backup_*.zip

# 4. Пересобрать и запустить
make server-build
make server-up
```

## Ограничения

- SQLite не предназначен для высоконагруженных production-сред
- Нет автоматического масштабирования
- Нет интеграции с внешними сервисами логирования
- LLM работает в режиме заглушки (stub) по умолчанию
