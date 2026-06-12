# Client Pilot Documentation Pack

Этот пакет документов предназначен для подготовки и проведения клиентского пилота Creative Test Agent.

## Состав

| Документ | Описание |
|----------|----------|
| `pilot_scope_ru.md` | Рамка пилота: цели, что входит/не входит, ограничения |
| `security_statement_ru.md` | Заявление о безопасности и закрытом контуре обработки |
| `technical_overview_ru.md` | Архитектура системы простым языком |
| `client_onboarding_questions_ru.md` | Вопросы для сбора требований клиента |
| `pilot_success_criteria_ru.md` | Критерии успешности пилота |
| `commercial_pilot_outline_ru.md` | Набросок коммерческого предложения |
| `pilot_profile_format_ru.md` | Формат pilot profile для загрузки конфигурации |

## Как использовать

1. Изучить `pilot_scope_ru.md` для понимания рамок пилота.
2. Использовать `client_onboarding_questions_ru.md` для встречи с клиентом.
3. Показать `security_statement_ru.md` для снятия вопросов о безопасности.
4. Показать `technical_overview_ru.md` для технической команды клиента.
5. Согласовать `pilot_success_criteria_ru.md` с клиентом.
6. Использовать `commercial_pilot_outline_ru.md` для коммерческого предложения.
7. Создать pilot profile под клиента и загрузить через `load_pilot_profile.py`.

## Сборка пакета

```bash
make build-client-pack
```

Пакет будет собран в `data/client_pilot_pack/`.
