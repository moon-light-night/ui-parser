# Фронтенд — UI Screenshot Analyzer

React SPA на Vite + TypeScript + Tailwind CSS + shadcn/ui.

Взаимодействует с бэкендом через gRPC-Web, проксируемый Envoy.

## Стек

- **React 19** + **TypeScript**
- **Vite** — сборщик и dev-сервер
- **Tailwind CSS** — утилитарные стили
- **shadcn/ui** — UI-примитивы
- **gRPC-Web** — связь с API-сервисом через Envoy

## Запуск в разработке

```bash
npm ci
npm run dev
```

Фронтенд доступен по адресу http://localhost:3000.
Запросы к API направляются на Envoy (http://localhost:8080).

## Сборка

```bash
npm run build
```

## Тесты

```bash
npm run test
```
