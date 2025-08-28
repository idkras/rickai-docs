# Rick.ai Documentation

Документация Rick.ai - AI-ассистированные проекты и интеграции.

## 🚀 Быстрый старт

1. Установите зависимости:
```bash
pip install mkdocs-material
```

2. Запустите локальный сервер:
```bash
mkdocs serve
```

3. Откройте http://127.0.0.1:8000

## ⚙️ Настройка GitHub Pages

Для правильной работы GitHub Pages без Actions:
- 📖 [Подробная инструкция](GITHUB_PAGES_SETUP.md)
- 🚀 [Быстрый старт](QUICK_START.md)

## 📚 Документация

- **Сайт**: https://idkras.github.io/rickai-docs/
- **GitHub**: https://github.com/idkras/rickai-docs

## 📞 Поддержка

- **Telegram**: @rick_ai
- **GitHub Issues**: Создать issue

## 🛠️ Разработка

### 🎯 Принцип работы

**Локальная сборка + Статические файлы на GitHub Pages**

1. **Сборка**: MkDocs собирает документацию локально в папку `site/`
2. **Деплой**: Статические HTML/CSS файлы отправляются в ветку `gh-pages`
3. **Отображение**: GitHub Pages показывает статику без дополнительной сборки

### Автоматические скрипты

**Быстрый деплой (рекомендуется):**
```bash
python mkdoc_gitpages_deploy.py
```

**Полный деплой (с установкой зависимостей):**
```bash
python deploy_docs.py
```

**Использование Makefile:**
```bash
make help          # Показать все команды
make install       # Установить зависимости
make build         # Собрать документацию
make serve         # Запустить локальный сервер
make quick-deploy  # Быстрый деплой
make deploy        # Полный деплой
```

### Ручные команды

```bash
# Сборка статических файлов
mkdocs build

# Деплой в ветку gh-pages
mkdocs gh-deploy --force
```
