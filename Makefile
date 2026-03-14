.DEFAULT_GOAL := help

.PHONY: install serve build publish clean help

install: ## Установить зависимости (первый запуск)
	poetry install

serve: ## Запустить локальный сервер с hot-reload → http://127.0.0.1:8000
	poetry run mkdocs serve

build: ## Собрать статический сайт в ./site/ (локальная проверка)
	poetry run mkdocs build

publish: ## Закоммитить всё и запушить → GitHub Actions задеплоит на Pages
	git add -A
	git commit -m "update: $$(date '+%Y-%m-%d %H:%M')" || echo "Нечего коммитить"
	git push origin main

clean: ## Удалить собранный сайт (./site/)
	rm -rf site/

help: ## Показать список доступных команд
	@echo "  make install    Установить зависимости (первый запуск)"
	@echo "  make serve      Локальный сервер с hot-reload → http://127.0.0.1:8000"
	@echo "  make build      Собрать сайт в ./site/ (локальная проверка)"
	@echo "  make publish    Коммит + push → GitHub Actions деплоит на Pages"
	@echo "  make clean      Удалить ./site/"
	@echo "  make help       Показать этот список"
