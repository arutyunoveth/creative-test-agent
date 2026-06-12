# Guided Demo Flow

## Пошаговая демонстрация системы

### Как открыть

1. Запустите сервер: `make run`
2. Откройте http://localhost:8000/ui/demo

### 10 шагов демо

| Шаг | Действие | Статус |
|-----|----------|--------|
| 1 | Load demo profile — загрузить профиль NovaBank | not_started / completed |
| 2 | Open NovaBank client — просмотреть клиента | missing / completed |
| 3 | Open project workspace — открыть проект | missing / completed |
| 4 | Upload/read brandbook — загрузить брендбук | missing / available / completed |
| 5 | Review A/B/C creatives — просмотреть креативы | missing / available / completed |
| 6 | Run batch test — запустить batch-тест | missing / available / completed |
| 7 | Open campaign summary — открыть сводку | missing / available / completed |
| 8 | Export DOCX/PPTX/PDF-ready — экспортировать отчёт | missing / available / completed |
| 9 | Create review — создать рецензию | missing / available / completed |
| 10 | Save feedback to knowledge — сохранить в базу знаний | available / completed |

### Быстрые действия

- **Load demo profile** — загружает NovaBank demo profile
- **Create demo batch** — создаёт и запускает batch-тест NovaBank A/B/C
- **View batches** — открывает список batch-запусков
- **View evaluations** — открывает страницу оценки качества

### Маршрут демонстрации

```
Dashboard (/)
→ Guided Demo (/ui/demo)
→ Clients (/ui/clients)
→ Project Workspace (/ui/projects)
→ Batch Test (/ui/batches)
→ Report (/ui/reports/{id})
→ Export (/ui/exports)
→ Review (/ui/reviews)
→ Knowledge Base (/ui/knowledge-base)
```
