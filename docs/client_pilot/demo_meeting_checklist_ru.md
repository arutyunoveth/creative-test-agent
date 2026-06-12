# Чеклист перед демо клиенту

## За день до демо

- [ ] Убедиться, что `make run` запускается без ошибок
- [ ] `make load-demo-profile` — demo-данные загружены
- [ ] `make pilot-check` — PASS
- [ ] `make check-server` — PASS
- [ ] `make release-check` — PASS
- [ ] `make pilot-smoke` — PASS
- [ ] `python scripts/run_demo_batch.py` — batch-тест завершён
- [ ] Проверить Guided Demo: http://localhost:8000/ui/demo — все шаги доступны
- [ ] Проверить Dashboard: http://localhost:8000/ — pilot readiness panel зелёная
- [ ] Версия 0.1.0-rc1 отображается в footer и на /version
- [ ] Сделать свежий backup: `python scripts/backup_data.py`

## За час до демо

- [ ] `make run` — сервер работает
- [ ] Открыть http://localhost:8000/ — dashboard загружается
- [ ] Проверить Clients, Projects, Creative Assets, Brandbooks — данные есть
- [ ] Открыть Guided Demo — все шаги completed
- [ ] Экспортировать тестовый report (DOCX/PPTX/PDF-ready) — проверить что файл создаётся
- [ ] Закрыть лишние вкладки браузера
- [ ] Выключить уведомления на рабочем столе

## Во время демо

- [ ] Начать с Dashboard — показать pilot readiness
- [ ] Показать Guided Demo — пошаговый workflow
- [ ] Показать Clients → Project → Creative Assets
- [ ] Показать Brandbook и его ingestion
- [ ] Показать Batch-тест и сводку
- [ ] Показать Report и Export
- [ ] Показать Review workflow
- [ ] Показать Knowledge Base
- [ ] Подчеркнуть local-only (данные не уходят)
- [ ] Рассказать про ограничения (честно)

## Что показать

1. Dashboard с pilot readiness panel
2. Guided Demo — 10-step flow
3. NovaBank client → проект → креативы A/B/C
4. Brandbook → ingestion результат
5. Batch-тест → Queue → Run All → Summary
6. Campaign summary → scores, risks, best creative
7. Report → Export DOCX/PPTX/PDF-ready
8. Create Review → Approve/Changes/Reject
9. Knowledge Base → сохранённый feedback
10. Release manifest → no_cloud_sdks: true

## Какие вопросы задать

- Какие типы креативов вы тестируете?
- Какие критерии оценки важны для вашей команды?
- Какой объём кампаний в месяц?
- Какой у вас процесс ревью сейчас?
- Используете ли вы уже LLM? Какие?
- Есть ли требования по compliance и локальности данных?
- Какой горизонт пилота?

## Что отправить после демо

- Client pilot pack (`data/client_pilot_pack.zip`)
- Release manifest (`data/release/release_manifest.json`)
- Ссылку на репозиторий
- Документацию (product overview, operator guide)
- Запись демо (если была)

## Что зафиксировать как next steps

- Решение о пилоте (да/нет/нужно больше информации)
- Состав пилотной группы
- Сроки пилота
- Дополнительные требования
- Ключевые контакты с обеих сторон
