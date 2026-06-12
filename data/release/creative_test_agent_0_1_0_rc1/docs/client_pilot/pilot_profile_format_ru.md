# Формат Pilot Profile

## Зачем нужен pilot profile

Pilot profile — это JSON-файл, который описывает конфигурацию пилота: бренд, аудитории, рубрику оценки и креативы. Профиль можно загрузить в систему одной командой, что обеспечивает повторяемость и лёгкую настройку под нового клиента.

## Структура JSON

```json
{
  "profile_name": "уникальное_имя_профиля",
  "demo": false,
  "description": "Описание профиля",
  "brand": {
    "name": "Название бренда",
    "tone_of_voice": "Описание tone of voice",
    "target_audience": "Целевая аудитория",
    "restrictions": "Ограничения и запрещённые формулировки",
    "claims_policy": "Политика в отношении claims"
  },
  "audiences": [
    {
      "name": "Название сегмента",
      "segment_description": "Описание сегмента",
      "pains": "Боли аудитории",
      "motivations": "Мотивация",
      "objections": "Возражения"
    }
  ],
  "rubric": {
    "name": "Название рубрики",
    "criteria": [
      {"name": "название_критерия", "description": "Описание"}
    ],
    "scale_min": 1,
    "scale_max": 10
  },
  "creative_assets": [
    {
      "title": "Название креатива",
      "asset_type": "text",
      "text_content": "Текст креатива",
      "variant": "A",
      "variant_description": "описание варианта"
    }
  ],
  "report_preferences": {
    "default_mode": "internal",
    "formats": ["markdown", "html"]
  }
}
```

## Поля

### `profile_name`
Уникальное имя профиля. Используется для idempotent-загрузки (повторная загрузка не создаёт дубликатов).

### `demo`
Если `true`, все сущности помечаются меткой `demo: true`, что позволяет сбросить их через `reset_demo_data.py`.

### `brand`
Обязательное поле. Бренд-профиль создаётся всегда.

### `audiences`
Массив аудиторных профилей. Может быть пустым.

### `rubric`
Обязательное поле. Рубрика оценки с критериями. Если не указаны критерии, используются стандартные (8 criteria).

### `creative_assets`
Массив текстовых креативов. Может быть пустым. Изображения и PDF загружаются отдельно через UI.

### `report_preferences`
Настройки отчётов по умолчанию.

## Как создать профиль под клиента

1. Скопировать `config/pilot_profiles/client_pilot_template.json` в новый файл.
2. Заполнить поля бренда, аудиторий, рубрики.
3. Указать уникальное `profile_name`.
4. Добавить креативы, если есть.
5. Загрузить профиль:

```bash
python scripts/load_pilot_profile.py config/pilot_profiles/мой_клиент.json
```

## Как загрузить профиль

```bash
# Загрузить демо-профиль NovaBank
python scripts/load_pilot_profile.py config/pilot_profiles/novabank_demo.json

# Загрузить профиль клиента
python scripts/load_pilot_profile.py config/pilot_profiles/client_pilot_template.json
```

При повторной загрузке профиля с тем же `profile_name` новые сущности не создаются (idempotent).

## Как проверить данные в UI

1. Запустить сервер: `make run`.
2. Открыть `http://localhost:8000/`.
3. Перейти в соответствующие разделы (Brand Profiles, Audience Profiles).
4. Убедиться, что данные загружены.

## Ограничения

- Загружаются только текстовые креативы. Изображения и PDF нужно загружать через UI.
- При повторной загрузке профиля с новыми креативами существующие не обновляются (только создаются новые).
- Пустой шаблон (`client_pilot_template.json`) валидируется, но не создаёт пустые сущности без brand name.
