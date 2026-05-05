.PHONY: up down restart build

up:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

build:
	docker compose build
