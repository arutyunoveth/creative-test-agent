# Final Pilot Checklist

## 1. Окружение настроено
- [ ] `python -m venv .venv && source .venv/bin/activate`
- [ ] `pip install -r requirements.txt`
- [ ] `make run` запускается без ошибок

## 2. Demo-данные загружены
- [ ] `make load-demo-profile` выполнен успешно
- [ ] Клиент NovaBank отображается в списке
- [ ] Проект NovaBank Campaign отображается
- [ ] Креативы A/B/C загружены
- [ ] Брендбук загружен и проиндексирован

## 3. Stub-режим работает
- [ ] `make eval-stub` — PASS
- [ ] `CTA_LLM_PROVIDER=stub` — batch-тест завершается успешно

## 4. Тесты проходят
- [ ] `pytest` — все тесты PASS
- [ ] `make pilot-check` — PASS
- [ ] `make check-server` — PASS
- [ ] `make client-pilot-check` — PASS

## 5. Релизный манифест
- [ ] `make release-manifest` создаёт `data/release/release_manifest.json`
- [ ] `make release-check` — PASS

## 6. Клиентский пакет
- [ ] `make build-client-pack` создаёт `data/client_pilot_pack.zip`
- [ ] Пакет включает документацию и скрипты

## 7. Резервное копирование
- [ ] `python scripts/backup_data.py` создаёт backup
- [ ] `python scripts/check_backup.py` — PASS

## 8. Guided demo
- [ ] http://localhost:8000/ui/demo — загружается
- [ ] Load demo profile — работает
- [ ] Create demo batch — работает

## 9. Локальность проверена
- [ ] Нет cloud SDK в зависимостях
- [ ] Нет внешних API вызовов
- [ ] `make release-manifest` показывает `no_cloud_sdks: true`

## 10. Документация
- [ ] `docs/product_overview_ru.md` — существует
- [ ] `docs/operator_guide_ru.md` — существует
- [ ] `docs/final_pilot_checklist_ru.md` — существует

## 11. Готовность к демонстрации
- [ ] Все пункты выше выполнены
- [ ] Клиентский пакет передан заказчику
- [ ] Вопросы по пилоту подготовлены
