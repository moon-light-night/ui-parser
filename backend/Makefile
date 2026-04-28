PYTHON = python3
VENV = venv
VENV_BIN = $(VENV)/bin
PYTHON_VENV = $(VENV_BIN)/python
PIP_VENV = $(VENV_BIN)/pip
UVICORN_VENV = $(VENV_BIN)/uvicorn

.PHONY: help venv install run dev clean test shell

venv: ## Создать виртуальное окружение
	@echo "Создание виртуального окружения..."
	$(PYTHON) -m venv $(VENV)
	@echo "Виртуальное окружение создано. Активируйте его с помощью: source $(VENV)/bin/activate"

install: venv ## Установить зависимости
	@echo "Установка зависимостей..."
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements.txt -r requirements-test.txt
	@echo "Зависимости установлены"

run: install ## Запустить сервер в production режиме
	@echo "Запуск сервера..."
	$(UVICORN_VENV) app.main:app --host 0.0.0.0 --port 8000

dev: install ## Запустить сервер в режиме разработки с перезагрузкой
	@echo "Запуск сервера в режиме разработки..."
	$(UVICORN_VENV) app.main:app --reload --host 0.0.0.0 --port 8000

clean: ## Очистить временные файлы и виртуальное окружение
	@echo "Очистка..."
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Очистка завершена"

test: install ## Запустить тесты
	@echo "Запуск тестов..."
	$(PYTHON_VENV) -m pytest tests/ -v

shell: install ## Запустить Python shell с настройками приложения
	@echo "Запуск Python shell..."
	$(PYTHON_VENV) -c "import sys; sys.path.insert(0, '.'); from app.main import app; print('FastAPI app импортирован. Доступен как app')" && $(PYTHON_VENV)

.DEFAULT_GOAL := help