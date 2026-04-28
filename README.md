# UI Screenshot Analyzer

Инструмент для анализа скриншотов интерфейса с помощью мультимодального LLM и общения с AI по контексту скриншотов.

---

## Архитектура

```
Browser (React + grpc-web)
        │
        ▼  HTTP/1.1 (gRPC-Web)
Envoy (port 8080)
        │
        ▼  gRPC
API service  (Python, port 50051)
  ├── Postgres (SQLAlchemy, Alembic)
  ├── MinIO S3 (presigned upload/download)
  └── Analyzer service (internal gRPC, port 50061)
            └── Ollama HTTP API (optional, port 11434)
```

| Сервис       | Технология                                                 |
|--------------|------------------------------------------------------------|
| Frontend     | React 19, TypeScript, Vite, Tailwind, shadcn/ui, gRPC-Web  |
| API          | Python 3.10, gRPC, FastAPI, SQLAlchemy 2, psycopg          |
| Analyzer     | Python 3.10, gRPC, Pydantic, httpx                         |
| Database     | Postgres 16                                                |
| Object store | MinIO (S3-compatible)                                      |
| Gateway      | Envoy 1.31.2                                               |
| AI           | Ollama (локально)                                          |

---

## Быстрый старт

### Требования
- Docker Desktop (или Docker Engine + Compose plugin)
- `git`
- Ollama (опционально)

### Запуск

```bash
git clone <repo-url>
cd ui-parser
cp .env.example .env   # измените при необходимости или оставьте значения по умолчанию для локальной разработки
docker compose up --build -d
```

Откройте http://localhost:3000 в браузере.

| URL                           | Описание                                     |
|-------------------------------|----------------------------------------------|
| http://localhost:3000         | React SPA                                    |
| http://localhost:8080         | Envoy (gRPC-Web gateway)                     |
| http://localhost:9001         | Консоль MinIO (учётные данные из `.env`)     |
| http://localhost:8000/health  | Проверка работоспособности API               |

---

## Настройка анализа через Ollama

По умолчанию анализатор работает в **режиме заглушки** (детерминированные тестовые ответы).
Чтобы использовать мультимодальный LLM:

1. Установите [Ollama](https://ollama.com) и загрузите небольшую мультимодальную модель, например `gemma4:e4b`:
   ```bash
   ollama pull gemma4:e4b
   ```
  Или выполните вход в учетную запись [Ollama](https://ollama.com) и используйте более мощную облачную модель, например `gemma4:31b-cloud` без необходимости загрузки на локальное устройство:
  ```bash
   ollama run gemma4:31b-cloud
   ```
2. Убедитесь, что Ollama запущена на хост-машине (по умолчанию `http://localhost:11434`).
3. При необходимости отключить Ollama и использовать заглушку - откройте `docker-compose.yml` и измените:
   ```yaml
   ANALYZER_MODE: stub
   ```
4. Перезапустите сервис анализатора:
   ```bash
   docker compose up --build analyzer
   ```

Доступные переменные окружения для анализатора:

| Переменная            | По умолчанию                            | Описание                                   |
|-----------------------|-----------------------------------------|--------------------------------------------|
| `ANALYZER_MODE`       | `stub`                                  | `stub` или `ollama`                        |
| `OLLAMA_BASE_URL`     | `http://host.docker.internal:11434`     | Базовый URL Ollama HTTP API                |
| `OLLAMA_MODEL`        | `gemma4:e4b`                            | Модель по умолчанию для всех задач         |
| `OLLAMA_VISION_MODEL` | (наследует `OLLAMA_MODEL`)              | Модель для анализа изображений             |
| `OLLAMA_CHAT_MODEL`   | (наследует `OLLAMA_MODEL`)              | Модель для ответов в чате                  |
| `OLLAMA_TIMEOUT`      | `120`                                   | Таймаут HTTP в секундах                    |

---

## Переменные окружения фронтенда

Переменная `VITE_APP_GRPC_BASE_URL` задаёт базовый URL Envoy gRPC-Web прокси и **вшивается в статику на этапе сборки** (Vite build-time).

| Переменная                  | По умолчанию              | Описание                                                                |
|-----------------------------|---------------------------|-------------------------------------------------------------------------|
| `VITE_APP_GRPC_BASE_URL`    | `http://localhost:8080`   | Базовый URL Envoy. При Docker-сборке берётся из корневого `.env`        |
| `VITE_APP_S3_PUBLIC_URL`    | `http://localhost:9000`   | Публичный URL MinIO/S3 для отображения превью скриншотов в браузере     |

Переменная необязательна - если не задана, используется `http://localhost:8080`.  
При Docker-сборке значение передаётся как build arg из корневого `.env`.

---

## Пользовательские сценарии

### Загрузка скриншота
1. Нажмите **Загрузить** в правом верхнем углу списка скриншотов.
2. Выберите файл PNG, JPEG или WebP (максимум 20 МБ).
3. Файл загружается напрямую в MinIO через presigned URL.
4. Нажмите **Анализировать** на странице скриншота, чтобы запустить AI-анализ.

### Чат по скриншоту
1. Откройте любой скриншот с завершённым анализом.
2. Нажмите **Новый чат**, чтобы начать беседу.
3. Введите сообщение - AI использует скриншот и его анализ как контекст.
4. Для одного скриншота можно создать несколько независимых сессий.

---

## Запуск тестов

### Бэкенд (API service)

```bash
cd backend
make venv
source venv/bin/activate
make install
make test
deactivate
```

### Сервис анализатора

```bash
cd services/analyzer
make venv
source venv/bin/activate
make install
make test
deactivate
```

### Фронтенд

```bash
cd frontend
npm i
npm run test
```

---

## Структура проекта

```
services/
  analyzer/           - внутренний gRPC-анализатор + клиент Ollama
    app/
      analyzer_service.py   - gRPC servicer
      ollama_client.py      - HTTP-вызовы к Ollama
      output_schema.py      - Pydantic-модели
      prompts.py            - фабрика промптов
    tests/
backend/               - публичный gRPC API service
  app/
    grpc/              - gRPC-сервер, сервисеры (screenshot_service.py, chat_service.py) и сгенерированные заглушки
    models/            - SQLAlchemy-модели
    storage.py         - вспомогательные функции presigned URL для MinIO
    redis_client.py    - клиент Redis для потоков чата
  tests/
frontend/
  src/
    grpc/              - gRPC-Web клиенты + сгенерированные типы
    pages/             - основные страницы приложения
    components/        - основные компоненты и UI-примитивы
      __tests__/       - тесты компонентов (Vitest)
    hooks/
      __tests__/       - тесты хуков (Vitest)
proto/                 - файлы контрактов .proto
infra/
  envoy.yaml           - конфигурация Envoy gRPC-Web прокси
docker-compose.yml
```

---

## Примечания

- Frontend общается с бэкендом исключительно через gRPC-Web посредством Envoy.  
- Backend скачивает изображение из MinIO перед передачей байтов анализатору.  
- Результаты анализа сохраняются в виде JSONB в Postgres; схема Pydantic в `output_schema.py` валидирует и нормализует вывод модели.  
- Контекст чата строится на основе последнего сохранённого анализа в виде дайджеста системного промпта; векторная база данных не используется.
