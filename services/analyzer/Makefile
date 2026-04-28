PYTHON = python3
VENV = venv
VENV_BIN = $(VENV)/bin
PYTHON_VENV = $(VENV_BIN)/python
PIP_VENV = $(VENV_BIN)/pip
UVICORN_VENV = $(VENV_BIN)/uvicorn

.PHONY: venv install run dev clean test

venv: ## Создать виртуальное окружение
	@echo "Создание виртуального окружения..."
	$(PYTHON) -m venv $(VENV)
	@echo "Виртуальное окружение создано. Активируйте его с помощью: source $(VENV)/bin/activate"

install: venv ## Установить зависимости
	@echo "Установка зависимостей..."
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements.txt
	$(PIP_VENV) install pytest pytest-asyncio
	@echo "Зависимости установлены"

run: install ## Запустить сервис
	@echo "Запуск analyzer..."
	$(UVICORN_VENV) app.main:app --host 0.0.0.0 --port 8001

dev: install ## Запустить сервис в режиме разработки с автоперезагрузкой
	@echo "Запуск analyzer в режиме разработки..."
	$(UVICORN_VENV) app.main:app --reload --host 0.0.0.0 --port 8001

test: install ## Запустить тесты
	@echo "Запуск тестов..."
	$(PYTHON_VENV) -m pytest tests/ -v

clean: ## Очистить временные файлы и виртуальное окружение
	@echo "Очистка..."
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Очистка завершена"

.DEFAULT_GOAL := help
