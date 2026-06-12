# Creative Test Agent — Руководство оператора

## Установка
1. Клонировать репозиторий:
   ```bash
   git clone <repo-url>
   cd creative-test-agent
   ```
2. Создать виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   ```
3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Запуск
```bash
make run
```
Открыть http://localhost:8000/

## Загрузка demo-профиля
```bash
make load-demo-profile
```
Загружает клиента NovaBank, проект, креативы A/B/C и брендбук.

## Создание клиента и проекта
Через UI:
1. Нажать "New Client", заполнить название и описание.
2. В карточке клиента нажать "New Project".
3. Указать название проекта.

## Загрузка брендбука
1. Перейти в Brandbooks → Upload Brandbook.
2. Выбрать PDF/DOCX/TXT файл, указать проект.
3. Нажать "Ingest" после загрузки.

## Запуск batch-теста
```bash
make run-demo-batch
```
Или через UI: Batches → New Batch → Queue → Run All.

## Экспорт отчёта
На странице отчёта нажать DOCX, PPTX или PDF-ready.

## Резервное копирование
```bash
python scripts/backup_data.py
```

## Релизный манифест
```bash
make release-manifest
```

## Проверка готовности
```bash
make release-check
make pilot-check
make check-server
make client-pilot-check
```

## Устранение неполадок
- **Ошибка подключения к БД**: проверить `data/` директория существует и доступна для записи.
- **LLM не отвечает**: проверить `CTA_LLM_PROVIDER=stub` для тестов или запустить Ollama.
- **Тесты падают**: `make pilot-check` покажет детали.
