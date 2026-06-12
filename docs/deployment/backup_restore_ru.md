# Резервное копирование и восстановление

## Скрипты

| Скрипт | Назначение |
|--------|-----------|
| `scripts/backup_data.py` | Создание backup-архива |
| `scripts/restore_data.py` | Восстановление из backup-архива |
| `scripts/check_backup.py` | Проверка целостности backup-архива |

## Создание backup

```bash
# Локально
python scripts/backup_data.py

# Через Docker
make server-backup
```

Backup создаётся в `CTA_BACKUP_ROOT` (по умолчанию `./data/backups`) с именем:

```
cta_backup_YYYYMMDD_HHMMSS.zip
```

### Состав backup-архива

- Файл SQLite базы данных
- Папка `storage/` (загруженные файлы, если `CTA_BACKUP_INCLUDE_UPLOADS=true`)
- Папка `exports/` (экспортированные документы, если `CTA_BACKUP_INCLUDE_EXPORTS=true`)
- `manifest.json` — метаданные и счётчики сущностей

### Что НЕ входит в backup

- `.env` файлы и секреты
- Сессионные cookie
- Кэш
- Логи

## Проверка backup

```bash
python scripts/check_backup.py data/backups/cta_backup_20260101_120000.zip
```

Скрипт проверяет:
- Zip-архив читаемый
- `manifest.json` существует и валиден
- Файл базы данных присутствует
- Нет `.env` файлов внутри
- Нет path traversal записей
- Ожидаемые папки существуют

## Восстановление из backup

```bash
# Локально (остановите приложение сначала)
python scripts/restore_data.py data/backups/cta_backup_20260101_120000.zip

# С принудительным восстановлением (если приложение работает)
python scripts/restore_data.py data/backups/cta_backup_20260101_120000.zip --force

# Через Docker
make server-restore BACKUP=data/backups/cta_backup_20260101_120000.zip
```

### Что делает restore

1. Проверяет, запущено ли приложение (отказывается, если да, — используйте `--force`)
2. Проверяет структуру backup-архива
3. Автоматически создаёт pre-restore backup
4. Восстанавливает базу данных, storage, exports
5. НЕ восстанавливает `.env` файлы

## Команды Makefile

```bash
make server-backup    # Создать backup в Docker
make server-restore   # Восстановить backup в Docker (требует BACKUP=...)
```

## Важно

- При восстановлении текущие данные заменяются данными из backup
- Перед restore автоматически создаётся backup текущего состояния
- SQLite не поддерживает параллельные операции — остановите приложение перед restore
