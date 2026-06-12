# Чеклист проверки сервера перед демо

## 1. Базовая проверка

- [ ] `make test` — все тесты проходят
- [ ] `make pilot-check` — проходит
- [ ] `make client-pilot-check` — проходит
- [ ] `make check-server` — проходит

## 2. Проверка closed-loop

- [ ] Cloud SDK пакеты не установлены
- [ ] `CTA_LOCAL_ONLY_MODE=true`
- [ ] `CTA_ALLOW_CLOUD_LLM=false`
- [ ] LLM provider — stub или локальный
- [ ] Vision provider — stub или локальный

## 3. Проверка эндпоинтов

- [ ] `GET /health` — 200 OK
- [ ] `GET /health/db` — database connected
- [ ] `GET /llm/health` — LLM health
- [ ] `GET /vision/health` — vision health

## 4. Проверка данных

- [ ] База данных доступна
- [ ] Storage root доступен для записи
- [ ] Миграции применены (если есть)
- [ ] Demo seed загружен

## 5. Client pack

- [ ] `make build-client-pack` собирает архив
- [ ] Pilot profile загружается

## 6. Проверка auth (если включена)

- [ ] `CTA_ENABLE_AUTH=true` и `CTA_SECRET_KEY` установлен
- [ ] Bootstrap admin создан (`python scripts/bootstrap_admin.py`)
- [ ] `GET /auth/me` возвращает пользователя
- [ ] `POST /auth/login` — логин работает
- [ ] `POST /auth/logout` — логаут работает
- [ ] Доступ к `/users` только у admin
- [ ] UI login page работает (`GET /ui/login`)

## 7. Ограничения

- [ ] Клиент предупреждён, что auth отключена (если `CTA_ENABLE_AUTH=false`)
- [ ] Клиент предупреждён, что SQLite не для production
- [ ] Клиент предупреждён, что stub режим не использует AI
- [ ] При auth=false нет разграничения прав
