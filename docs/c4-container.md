# C4 Container Diagram - UI Screenshot Analyzer

C4 Container раскрывает внутренние контейнеры системы, их технологии и способы взаимодействия.

## Диаграмма

```mermaid
C4Container
    title C4 Container - UI Screenshot Analyzer

    Person(user, "Пользователь", "Работает через браузер")
    System_Ext(ollama, "Ollama", "Локальный LLM / VLM сервер на хост-машине. gemma4:e4b, gemma4:31b-cloud и другие модели.")

    System_Boundary(boundary, "UI Screenshot Analyzer") {

        System_Boundary(frontend_gw, "Frontend & Gateway") {
            Container(spa, "React SPA", "React 19, TypeScript, Vite / Nginx", "Веб-интерфейс: загрузка скриншотов, просмотр анализа, чат-сессии. Общается с backend через gRPC-Web.")
            Container(envoy, "Envoy", "Envoy Proxy 1.31", "gRPC-Web → gRPC транслятор. Принимает HTTP/1.1 от браузера, проксирует gRPC (HTTP/2) на backend.")
        }

        System_Boundary(backend_svc, "Services") {
            Container(api, "API Service", "Python 3.10 · FastAPI + gRPC · SQLAlchemy 2", "Основной backend. Обрабатывает gRPC-вызовы: регистрация скриншотов, запуск анализа, чат-сессии. Генерирует presigned URL.")
            Container(analyzer, "Analyzer Service", "Python 3.10 · gRPC · Pydantic", "Внутренний сервис анализа. Скачивает файл из S3, отправляет в Ollama, возвращает структурированный JSON. Стримит ответы чата.")
        }

        System_Boundary(storage, "Storage") {
            ContainerDb(postgres, "PostgreSQL", "PostgreSQL 16", "Основная БД. Скриншоты, анализы, чат-сессии, сообщения.")
            ContainerDb(redis, "Redis", "Redis 7", "Временное состояние потоковых операций.")
            ContainerDb(minio, "MinIO", "MinIO · S3-compatible", "Объектное хранилище файлов скриншотов.")
        }
    }

    Rel(user, spa, "Открывает в браузере", "HTTPS")
    Rel(user, minio, "Загружает файл напрямую по presigned URL", "HTTPS PUT")

    Rel(spa, envoy, "ScreenshotService, ChatService, SystemService", "HTTP/1.1 · gRPC-Web")
    Rel(envoy, api, "Проксирует gRPC вызовы", "gRPC · HTTP/2")

    Rel(api, analyzer, "AnalyzeScreenshot, GenerateChatReply (stream)", "gRPC · HTTP/2")
    Rel(api, postgres, "Читает и записывает данные", "SQL · psycopg")
    Rel(api, redis, "Кеширует состояние потоков", "Redis protocol")
    Rel(api, minio, "Генерирует presigned URL, читает файлы", "S3 API · HTTP")

    Rel(analyzer, minio, "Скачивает файл скриншота", "S3 API · HTTP")
    Rel(analyzer, ollama, "Изображение + промпт → JSON / поток текста", "HTTP · Ollama REST API")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="3")
```

## Контейнеры

| Контейнер            | Технология                  | Порты                                | Описание                                                        |
|----------------------|-----------------------------|--------------------------------------|-----------------------------------------------------------------|
| **React SPA**        | React 19, TypeScript, Nginx | `3000`                               | Фронтенд, раздаётся Nginx в production-сборке                   |
| **Envoy**            | Envoy Proxy 1.31            | `8080`                               | gRPC-Web → gRPC прокси; единственная точка входа для gRPC       |
| **API Service**      | Python 3.10, FastAPI, gRPC  | `8000` (HTTP), `50051` (gRPC)        | Основной backend: бизнес-логика, БД, S3, оркестрация            |
| **Analyzer Service** | Python 3.10, gRPC           | `8010` (HTTP health), `50061` (gRPC) | Изолированный сервис анализа; единственный, кто вызывает Ollama |
| **PostgreSQL**       | PostgreSQL 16               | `5432`                               | Основное хранилище данных; миграции через Alembic               |
| **Redis**            | Redis 7                     | `6379`                               | Временное состояние; потенциальная очередь задач                |
| **MinIO**            | MinIO S3                    | `9000` (API), `9001` (консоль)       | Объектное хранилище файлов скриншотов                           |

## Внешние системы

| Система    | Где запускается                            | Протокол  |
|------------|--------------------------------------------|-----------|
| **Ollama** | Хост-машина (`host.docker.internal:11434`) | HTTP REST |

## Потоки данных

### Загрузка скриншота
```
Пользователь → API Service   (gRPC: CreateScreenshotUploadUrl)
API Service  → MinIO          (генерация presigned URL)
API Service  → Пользователь  (presigned URL)
Пользователь → MinIO          (PUT файла напрямую)
Пользователь → API Service   (gRPC: RegisterScreenshot)
API Service  → PostgreSQL     (INSERT screenshot)
```

### Анализ скриншота
```
Пользователь  → API Service   (gRPC: StartScreenshotAnalysis)
API Service   → Analyzer      (gRPC: AnalyzeScreenshot)
Analyzer      → MinIO          (скачать файл)
Analyzer      → Ollama         (HTTP: изображение + промпт)
Ollama        → Analyzer       (структурированный JSON)
Analyzer      → API Service   (AnalyzeScreenshotResponse)
API Service   → PostgreSQL     (INSERT analysis)
```

### Чат
```
Пользователь  → API Service   (gRPC stream: SendChatMessage)
API Service   → PostgreSQL     (INSERT user message)
API Service   → Analyzer      (gRPC stream: GenerateChatReply)
Analyzer      → Ollama         (HTTP stream: промпт + контекст анализа)
Ollama        → Analyzer       (потоковый текст)
Analyzer     ↪ API Service   ↪ Пользователь  (стриминг чанков)
API Service   → PostgreSQL     (INSERT assistant message)
```
