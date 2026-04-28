# UML Sequence Diagrams - UI Screenshot Analyzer

Три основных потока: загрузка скриншота, анализ и чат.

---

## 1. Загрузка скриншота

Файл загружается напрямую в S3 из браузера, минуя backend.

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant SPA as React SPA
    participant Envoy as Envoy
    participant API as API Service
    participant DB as PostgreSQL
    participant S3 as MinIO (S3)

    User->>SPA: Выбирает файл и нажимает Upload

    SPA->>Envoy: CreateScreenshotUploadUrl(filename, mime_type, size)
    Envoy->>API: CreateScreenshotUploadUrl(...)
    API->>S3: GeneratePresignedPutURL(object_key)
    S3-->>API: presigned_url, object_key, bucket
    API-->>Envoy: CreateScreenshotUploadUrlResponse
    Envoy-->>SPA: presigned_url, object_key, bucket

    SPA->>S3: PUT /bucket/object_key (тело файла)
    S3-->>SPA: 200 OK

    SPA->>Envoy: RegisterScreenshot(filename, mime_type, size, bucket, object_key)
    Envoy->>API: RegisterScreenshot(...)
    API->>DB: INSERT INTO screenshots
    DB-->>API: screenshot record
    API-->>Envoy: RegisterScreenshotResponse(screenshot_id, status=uploaded)
    Envoy-->>SPA: screenshot_id, status

    SPA-->>User: Скриншот появляется в списке
```

---

## 2. Анализ скриншота

Backend делегирует анализ внутреннему Analyzer Service, который обращается к Ollama.

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant SPA as React SPA
    participant Envoy as Envoy
    participant API as API Service
    participant DB as PostgreSQL
    participant Analyzer as Analyzer Service
    participant S3 as MinIO (S3)
    participant Ollama as Ollama

    User->>SPA: Открывает страницу скриншота / нажимает Analyze

    SPA->>Envoy: StartScreenshotAnalysis(screenshot_id)
    Envoy->>API: StartScreenshotAnalysis(...)
    API->>DB: UPDATE screenshots SET status=analyzing
    API->>Analyzer: AnalyzeScreenshot(screenshot_id, bucket, object_key)

    Analyzer->>S3: GetObject(bucket, object_key)
    S3-->>Analyzer: image bytes

    Analyzer->>Ollama: POST /api/generate (image + prompt, JSON mode)
    Note over Ollama: Мультимодальная модель<br/>обрабатывает изображение
    Ollama-->>Analyzer: structured JSON response

    Analyzer->>Analyzer: Валидация через Pydantic
    Analyzer-->>API: AnalyzeScreenshotResponse(result_json, summary, model_name)

    API->>DB: INSERT INTO analyses (result_json, summary, ...)
    API->>DB: UPDATE screenshots SET status=completed
    DB-->>API: ok

    API-->>Envoy: StartScreenshotAnalysisResponse(analysis_id)
    Envoy-->>SPA: analysis_id

    SPA->>Envoy: GetLatestScreenshotAnalysis(screenshot_id)
    Envoy->>API: GetLatestScreenshotAnalysis(...)
    API->>DB: SELECT * FROM analyses WHERE screenshot_id ORDER BY created_at DESC LIMIT 1
    DB-->>API: analysis record
    API-->>Envoy: GetLatestScreenshotAnalysisResponse(result_json, ...)
    Envoy-->>SPA: analysis data

    SPA-->>User: Отображает панель анализа
```

---

## 3. Чат по скриншоту

Ответ ассистента стримится чанками через server-streaming gRPC.

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant SPA as React SPA
    participant Envoy as Envoy
    participant API as API Service
    participant DB as PostgreSQL
    participant Analyzer as Analyzer Service
    participant Ollama as Ollama

    User->>SPA: Создаёт новую чат-сессию

    SPA->>Envoy: CreateChatSession(screenshot_id, title)
    Envoy->>API: CreateChatSession(...)
    API->>DB: INSERT INTO chat_sessions
    DB-->>API: session record
    API-->>Envoy: CreateChatSessionResponse(session_id)
    Envoy-->>SPA: session_id

    User->>SPA: Вводит сообщение и отправляет

    SPA->>Envoy: SendChatMessage(session_id, content) [server-stream]
    Envoy->>API: SendChatMessage(...) [server-stream]

    API->>DB: INSERT INTO chat_messages (role=user, content)
    API->>DB: SELECT анализ и историю сообщений сессии
    DB-->>API: analysis context + message history

    API->>Analyzer: GenerateChatReply(session_id, message_history, analysis_json) [server-stream]

    loop Стриминг ответа
        Analyzer->>Ollama: POST /api/chat (stream=true, messages + контекст)
        Ollama-->>Analyzer: chunk (текстовый фрагмент)
        Analyzer-->>API: GenerateChatReplyEvent(chunk)
        API-->>Envoy: SendChatMessageEvent(chunk)
        Envoy-->>SPA: SendChatMessageEvent(chunk)
        SPA-->>User: Текст появляется постепенно
    end

    Analyzer-->>API: GenerateChatReplyEvent(done=true, full_content)
    API->>DB: INSERT INTO chat_messages (role=assistant, content=full_content)
    API-->>Envoy: SendChatMessageEvent(done=true)
    Envoy-->>SPA: SendChatMessageEvent(done=true)

    SPA-->>User: Сообщение ассистента завершено
```
