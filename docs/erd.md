# Database Schema - Entity Relationship Diagram

Диаграмма описывает схему PostgreSQL базы данных сервиса UI Screenshot Analyzer.

## ENUMs

| Тип                 | Значения                                    |
|---------------------|---------------------------------------------|
| `screenshot_status` | `uploaded`, `analyzing`, `completed`, `failed` |
| `message_role`      | `user`, `assistant`, `system`               |
| `message_status`    | `completed`, `streaming`, `failed`          |

## ERD

```mermaid
erDiagram
    screenshots {
        uuid        id               PK
        varchar255  title            "nullable"
        varchar512  original_filename
        varchar128  mime_type
        integer     file_size
        varchar255  storage_bucket
        varchar1024 storage_key
        varchar64   storage_region   "nullable"
        text        storage_url      "nullable"
        enum        status           "screenshot_status · default uploaded"
        timestamptz created_at
        timestamptz updated_at
    }

    analyses {
        uuid     id             PK
        uuid     screenshot_id  FK
        varchar255 model_name
        text     summary        "nullable"
        jsonb    result_json    "nullable"
        text     error_message  "nullable"
        timestamptz created_at
        timestamptz updated_at
    }

    chat_sessions {
        uuid     id             PK
        uuid     screenshot_id  FK
        varchar512 title        "default New chat"
        timestamptz created_at
        timestamptz updated_at
    }

    chat_messages {
        uuid     id         PK
        uuid     session_id FK
        enum     role       "message_role"
        text     content
        enum     status     "message_status · default completed"
        varchar255 model_name "nullable"
        timestamptz created_at
    }

    screenshots ||--o{ analyses      : "1 : N (CASCADE DELETE)"
    screenshots ||--o{ chat_sessions  : "1 : N (CASCADE DELETE)"
    chat_sessions ||--o{ chat_messages : "1 : N (CASCADE DELETE)"
```

## Индексы

| Таблица        | Индекс                           | Колонки          |
|----------------|----------------------------------|------------------|
| `analyses`     | `ix_analyses_screenshot_id`      | `screenshot_id`  |
| `chat_sessions`| `ix_chat_sessions_screenshot_id` | `screenshot_id`  |
| `chat_messages`| `ix_chat_messages_session_id`    | `session_id`     |

## Описание связей

| Связь                             | Тип                        | ON DELETE | Примечание                                                                             |
|-----------------------------------|----------------------------|-----------|----------------------------------------------------------------------------------------|
| `screenshots` → `analyses`        | **один ко многим** (1 : N) | CASCADE   | Один скриншот - много запусков анализа; в приложении берётся последний по `created_at` |
| `screenshots` → `chat_sessions`   | **один ко многим** (1 : N) | CASCADE   | Один скриншот - много чат-сессий                                                       |
| `chat_sessions` → `chat_messages` | **один ко многим** (1 : N) | CASCADE   | Одна сессия - упорядоченный список сообщений (`user` / `assistant` / `system`)         |


## Хранилище файлов

Физические файлы скриншотов хранятся в **S3-совместимом хранилище** (MinIO в локальной разработке). В БД хранится только ссылка:

| Поле             | Описание                            |
|------------------|-------------------------------------|
| `storage_bucket` | Имя бакета (`screenshots`)          |
| `storage_key`    | Путь к объекту внутри бакета        |
| `storage_region` | Регион (опционально, `us-east-1`)   |
| `storage_url`    | Полный публичный URL (для отладки)  |

## Миграции

Схема управляется через **Alembic**. Миграции находятся в [`backend/alembic/versions/`](../backend/alembic/versions/).

```bash
# Применить все миграции
docker compose exec backend alembic upgrade head

# Создать новую миграцию
docker compose exec backend alembic revision --autogenerate -m "description"
```
