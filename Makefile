# Makefile для Rick.ai Documentation

.PHONY: help install build serve deploy quick-deploy clean test status push setup check-pages

# Цвета для вывода
GREEN = \033[0;32m
BLUE = \033[0;34m
RED = \033[0;31m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(BLUE)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(BLUE)Устанавливаем зависимости...$(NC)"
	pip install -r requirements.txt

build: ## Собрать документацию
	@echo "$(BLUE)Собираем документацию...$(NC)"
	mkdocs build

serve: ## Запустить локальный сервер
	@echo "$(BLUE)Запускаем локальный сервер...$(NC)"
	mkdocs serve

deploy: ## Полный деплой (с установкой зависимостей)
	@echo "$(BLUE)Запускаем полный деплой...$(NC)"
	python deploy_docs.py

quick-deploy: ## Быстрый деплой (без установки зависимостей)
	@echo "$(BLUE)Запускаем быстрый деплой...$(NC)"
	python quick_deploy.py

clean: ## Очистить собранную документацию
	@echo "$(YELLOW)Очищаем собранную документацию...$(NC)"
	rm -rf site/

test: ## Проверить конфигурацию
	@echo "$(BLUE)Проверяем конфигурацию...$(NC)"
	mkdocs serve --strict

status: ## Показать статус git
	@echo "$(BLUE)Статус git:$(NC)"
	git status

push: ## Отправить изменения в репозиторий
	@echo "$(BLUE)Отправляем изменения...$(NC)"
	git add .
	git commit -m "Update documentation $(shell date '+%Y-%m-%d %H:%M:%S')"
	git push origin main

setup: install build ## Первоначальная настройка
	@echo "$(GREEN)Настройка завершена!$(NC)"
	@echo "$(BLUE)Запустите 'make serve' для просмотра документации$(NC)"

check-pages: ## Проверить статус GitHub Pages
	@echo "$(BLUE)Проверяем статус GitHub Pages...$(NC)"
	python3 check_pages.py
