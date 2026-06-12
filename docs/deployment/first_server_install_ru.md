# Первая установка Creative Test Agent на сервер

## Что понадобится

- Сервер с Linux (Ubuntu 22.04+ / Debian 12+) или macOS
- Установленные: Git, Python 3.11+, Docker (опционально)
- Доступ к локальному LLM (Ollama, LM Studio) — или stub-режим для демо
- Минимум 8GB RAM, 20GB свободного места на диске

## Что копируем на сервер

```bash
# Вариант 1: Клонировать репозиторий
git clone <repo-url>
cd creative-test-agent

# Вариант 2: Распаковать release bundle
unzip creative_test_agent_0.1.0-rc1.zip -d creative-test-agent
cd creative-test-agent
```

## Как создать .env.server

```bash
cp .env.server.example .env.server
```

Отредактировать `.env.server`:

```ini
CTA_ENV=server
CTA_SECRET_KEY=<сгенерировать случайную строку>
CTA_ENABLE_AUTH=true
CTA_DATABASE_URL=sqlite:///data/cta.db
CTA_LLM_PROVIDER=ollama
CTA_LLM_BASE_URL=http://localhost:11434
CTA_LLM_MODEL=llama3.2
```

Для демо-режима без LLM:

```ini
CTA_LLM_PROVIDER=stub
CTA_VISION_PROVIDER=stub
CTA_ENABLE_AUTH=false
```

## Как собрать Docker image

```bash
make server-build
```

Или вручную:

```bash
docker compose -f docker-compose.server.yml build
```

## Как запустить

```bash
make server-up
```

Или:

```bash
docker compose -f docker-compose.server.yml up -d
```

Приложение будет доступно на http://localhost:8000

## Как создать admin

```bash
make server-bootstrap-admin
```

Или:

```bash
docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/bootstrap_admin.py
```

## Как проверить сервер

```bash
make server-check
```

Или открыть в браузере:

```
http://localhost:8000/health
http://localhost:8000/health/db
http://localhost:8000/version
```

## Как загрузить demo profile

```bash
docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/load_pilot_profile.py config/pilot_profiles/novabank_demo.json
```

## Как открыть Guided Demo

Открыть http://localhost:8000/ui/demo

## Как сделать backup

```bash
make server-backup
```

Или:

```bash
docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/backup_data.py
```

## Как обновляться

```bash
git pull
make server-build
make server-up
```

Если были изменения в БД:

```bash
docker compose -f docker-compose.server.yml exec creative-test-agent python scripts/run_migrations.py
```

## Как откатиться

```bash
git checkout <previous-tag>
make server-build
make server-up
```

Для восстановления данных из backup:

```bash
make server-restore BACKUP=/path/to/backup.zip
```

## Ограничения release candidate

- Не предназначено для production-нагрузки
- Рекомендуется для демо и пилота с 1-5 пользователями
- Регулярно делайте backup через скрипт
- Не удаляйте `data/` директорию вручную
