# Фронтенд — UI Screenshot Analyzer

React SPA на Vite + TypeScript + Tailwind CSS + shadcn/ui.

Взаимодействует с бэкендом через gRPC-Web, проксируемый Envoy.

## Стек

- **React 19** + **TypeScript**
- **Vite** — сборщик и dev-сервер
- **Tailwind CSS** — утилитарные стили
- **shadcn/ui** — UI-примитивы (компоненты в `src/components/ui/`, исключены из линтинга)
- **Zustand** — управление глобальным состоянием
- **gRPC-Web** — связь с API-сервисом через Envoy

## Управление состоянием

Глобальное состояние реализовано через [Zustand](https://github.com/pmndrs/zustand). Хранилища находятся в `src/store/`

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

## Проверка типов

```bash
npm run checkTypes
```

## Линтинг

```bash
npm run lint        
npm run lint:fix    
```

Из линтинга исключены:
- `src/proto/generated/**` — сгенерированные proto-клиенты
- `src/components/ui/**` — компоненты shadcn/ui

## Тесты

```bash
npm run test
```
